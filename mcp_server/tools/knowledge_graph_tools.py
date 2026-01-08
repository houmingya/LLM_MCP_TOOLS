"""
知识图谱工具模块
提供实体抽取、关系抽取、知识图谱构建和查询功能
支持持久化存储和增量更新
"""

import logging
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import networkx as nx
from openai import OpenAI
from config.settings import LLMConfig, KNOWLEDGE_GRAPH_DIR

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KnowledgeGraphTools:
    """知识图谱工具类 - 支持持久化和增量更新"""
    
    def __init__(self, storage_dir: Path = KNOWLEDGE_GRAPH_DIR):
        """
        初始化知识图谱
        
        Args:
            storage_dir: 持久化存储目录
        """
        self.storage_dir = storage_dir
        self.graph_file = storage_dir / "knowledge_graph.gpickle"  # NetworkX 图文件
        self.metadata_file = storage_dir / "metadata.json"  # 元数据文件
        
        # 使用 NetworkX 创建有向图
        self.graph = nx.DiGraph()
        
        # 初始化 OpenAI 客户端用于实体和关系抽取
        self.client = OpenAI(
            api_key=LLMConfig.API_KEY,
            base_url=LLMConfig.API_BASE
        )
        
        # 实体类型定义
        self.entity_types = [
            "公司/组织",
            "人物",
            "产品/服务",
            "技术/概念",
            "地点",
            "时间",
            "项目/方案"
        ]
        
        # 关系类型定义
        self.relation_types = [
            "任职于",
            "生产/提供",
            "位于",
            "属于",
            "使用",
            "合作",
            "参与",
            "拥有",
            "开发",
            "应用于"
        ]
        
        # 尝试从磁盘加载已有的知识图谱
        self.load_graph()
        
        logger.info(f"知识图谱工具初始化成功 - 节点数: {self.graph.number_of_nodes()}, 边数: {self.graph.number_of_edges()}")
    
    def save_graph(self) -> bool:
        """
        保存知识图谱到磁盘
        
        Returns:
            是否保存成功
        """
        try:
            # 保存图结构（使用 pickle）
            # 注意：新版 NetworkX 中 write_gpickle 已被移除，改用标准 pickle
            with open(self.graph_file, 'wb') as f:
                pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
            
            # 保存元数据
            metadata = {
                "nodes_count": self.graph.number_of_nodes(),
                "edges_count": self.graph.number_of_edges(),
                "entity_types": self.entity_types,
                "relation_types": self.relation_types,
                "last_updated": str(Path(self.graph_file).stat().st_mtime) if self.graph_file.exists() else None
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 知识图谱已保存: {self.graph.number_of_nodes()} 个节点, {self.graph.number_of_edges()} 条边")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存知识图谱失败: {str(e)}")
            return False
    
    def load_graph(self) -> bool:
        """
        从磁盘加载知识图谱
        
        Returns:
            是否加载成功
        """
        try:
            if self.graph_file.exists():
                # 加载图结构
                with open(self.graph_file, 'rb') as f:
                    self.graph = pickle.load(f)
                logger.info(f"✅ 从磁盘加载知识图谱: {self.graph.number_of_nodes()} 个节点, {self.graph.number_of_edges()} 条边")
                return True
            else:
                logger.info("💡 未找到已保存的知识图谱，将创建新的空图")
                return False
                
        except Exception as e:
            logger.error(f"❌ 加载知识图谱失败: {str(e)}")
            self.graph = nx.DiGraph()  # 重新创建空图
            return False
    
    def clear_graph(self) -> Dict[str, Any]:
        """
        清空知识图谱（慎用！）
        
        Returns:
            清空结果
        """
        try:
            old_nodes = self.graph.number_of_nodes()
            old_edges = self.graph.number_of_edges()
            
            self.graph.clear()
            self.save_graph()
            
            return {
                "success": True,
                "message": f"知识图谱已清空（原有 {old_nodes} 个节点, {old_edges} 条边）"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """
        使用大模型从文本中抽取实体和关系
        
        Args:
            text: 待分析的文本
            
        Returns:
            包含实体和关系的字典
        """
        try:
            prompt = f"""请分析以下文本，提取出所有的实体和它们之间的关系。

                    文本内容：
                    {text}

                    请按照以下JSON格式返回结果（必须是严格的JSON格式，不要有注释，不要有多余的逗号）：
                    {{
                        "entities": [
                            {{"name": "实体名称", "type": "实体类型", "description": "简短描述"}}
                        ],
                        "relations": [
                            {{"source": "源实体", "target": "目标实体", "relation": "关系类型", "description": "关系描述"}}
                        ]
                    }}

                    实体类型包括：{', '.join(self.entity_types)}
                    关系类型包括：{', '.join(self.relation_types)}

                    重要规则：
                    1. 只提取重要的实体，避免提取过于细碎的信息
                    2. **【关键】关系中的source和target必须与entities中的name完全一致（包括标点符号、空格）**
                    3. **【关键】在添加relations之前，先检查source和target是否都在entities列表中存在**
                    4. 返回纯JSON格式，不要添加```json```标记
                    5. 所有字符串必须用双引号，不要用单引号
                    6. 不要在JSON中添加注释
                    7. 最后一个元素后面不要有逗号

                    示例：
                    如果entities中有 {{"name": "AI视频分析系统", ...}}
                    那么relations中应该用 {{"source": "AI视频分析系统", ...}} 
                    而不是 {{"source": "AI分析系统", ...}}
                    """

            response = self.client.chat.completions.create(
                model=LLMConfig.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识图谱构建助手，擅长从文本中抽取实体和关系。返回结果必须是严格的JSON格式。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}  # 强制返回JSON格式
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"大模型原始返回（前500字符）: {result_text[:500]}")
            
            # 尝试提取JSON（处理可能的markdown包装）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # 清理可能的格式问题
            result_text = result_text.replace('\n', ' ').replace('\r', '')
            # 处理单引号（某些模型可能返回单引号）
            # result_text = result_text.replace("'", '"')
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                logger.error(f"问题文本: {result_text[:1000]}")
                
                # 尝试修复常见的JSON问题
                import re
                # 移除注释
                result_text = re.sub(r'//.*?\n', '', result_text)
                result_text = re.sub(r'/\*.*?\*/', '', result_text, flags=re.DOTALL)
                
                try:
                    result = json.loads(result_text)
                    logger.info("JSON修复成功")
                except:
                    logger.error("JSON修复失败，返回空结果")
                    return {"entities": [], "relations": [], "error": f"JSON解析失败: {str(e)}"}
            
            logger.info(f"提取了 {len(result.get('entities', []))} 个实体和 {len(result.get('relations', []))} 个关系")
            return result
            
        except Exception as e:
            logger.error(f"实体关系抽取失败: {str(e)}")
            return {"entities": [], "relations": [], "error": str(e)}
    
    def build_graph_from_document(self, content: str, filename: str) -> Dict[str, Any]:
        """
        从文档内容构建知识图谱
        
        Args:
            content: 文档内容
            filename: 文件名
            
        Returns:
            构建结果
        """
        try:
            # 如果文本过长，分段处理
            max_chunk_size = 2000
            chunks = []
            
            if len(content) > max_chunk_size:
                # 按段落分割
                paragraphs = content.split('\n')
                current_chunk = ""
                
                for para in paragraphs:
                    if len(current_chunk) + len(para) < max_chunk_size:
                        current_chunk += para + "\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = para + "\n"
                
                if current_chunk:
                    chunks.append(current_chunk)
            else:
                chunks = [content]
            
            all_entities = []
            all_relations = []
            
            # 处理每个文本块
            for i, chunk in enumerate(chunks):
                logger.info(f"处理文档 {filename} 的第 {i+1}/{len(chunks)} 块")
                result = self.extract_entities_and_relations(chunk)
                
                all_entities.extend(result.get('entities', []))
                all_relations.extend(result.get('relations', []))
            
            # 去重实体（基于名称）
            unique_entities = {}
            for entity in all_entities:
                name = entity['name']
                if name not in unique_entities:
                    unique_entities[name] = entity
                    # 添加来源文档信息
                    unique_entities[name]['source_document'] = filename
            
            # 添加实体到图中（增量更新，不覆盖已有实体）
            new_entities = 0
            updated_entities = 0
            
            for entity in unique_entities.values():
                entity_name = entity['name']
                
                if entity_name in self.graph.nodes:
                    # 实体已存在，更新信息（合并描述，保留来源文档）
                    existing_data = self.graph.nodes[entity_name]
                    
                    # 合并描述（如果新描述更详细）
                    old_desc = existing_data.get('description', '')
                    new_desc = entity.get('description', '')
                    if new_desc and (not old_desc or len(new_desc) > len(old_desc)):
                        self.graph.nodes[entity_name]['description'] = new_desc
                    
                    # 合并来源文档（追加）
                    old_docs = existing_data.get('source_document', '')
                    if filename not in old_docs:
                        self.graph.nodes[entity_name]['source_document'] = f"{old_docs}, {filename}" if old_docs else filename
                    
                    updated_entities += 1
                    logger.debug(f"🔄 更新实体: {entity_name}")
                else:
                    # 新实体，添加到图中
                    self.graph.add_node(
                        entity_name,
                        type=entity.get('type', 'Unknown'),
                        description=entity.get('description', ''),
                        source_document=filename
                    )
                    new_entities += 1
                    logger.debug(f"➕ 新增实体: {entity_name}")
            
            logger.info(f"实体处理完成: 新增 {new_entities} 个，更新 {updated_entities} 个，当前图中共有 {self.graph.number_of_nodes()} 个节点")
            
            # 添加关系到图中（增量更新，累积关系）
            added_relations = 0
            updated_relations = 0
            skipped_relations = []
            
            for relation in all_relations:
                source = relation.get('source')
                target = relation.get('target')
                relation_type = relation.get('relation', 'related_to')
                
                # 检查实体是否存在
                source_exists = source in self.graph.nodes
                target_exists = target in self.graph.nodes
                
                if source_exists and target_exists:
                    # 检查是否已存在相同的边
                    if self.graph.has_edge(source, target):
                        # 边已存在，检查是否相同关系类型
                        existing_edge = self.graph.edges[source, target]
                        existing_relation = existing_edge.get('relation', '')
                        
                        if relation_type == existing_relation:
                            # 相同关系，更新描述（合并）
                            old_desc = existing_edge.get('description', '')
                            new_desc = relation.get('description', '')
                            if new_desc and new_desc not in old_desc:
                                combined_desc = f"{old_desc}; {new_desc}" if old_desc else new_desc
                                self.graph.edges[source, target]['description'] = combined_desc
                            
                            # 更新来源文档
                            old_docs = existing_edge.get('source_document', '')
                            if filename not in old_docs:
                                self.graph.edges[source, target]['source_document'] = f"{old_docs}, {filename}" if old_docs else filename
                            
                            updated_relations += 1
                            logger.debug(f"🔄 更新关系: [{source}] --[{relation_type}]--> [{target}]")
                        else:
                            # 不同关系类型，在描述中追加新关系
                            existing_desc = existing_edge.get('description', '')
                            new_relation_desc = f"【{relation_type}】{relation.get('description', '')}"
                            
                            if new_relation_desc not in existing_desc:
                                combined_desc = f"{existing_desc}; {new_relation_desc}" if existing_desc else new_relation_desc
                                self.graph.edges[source, target]['description'] = combined_desc
                                self.graph.edges[source, target]['relation'] = f"{existing_relation}, {relation_type}"
                            
                            updated_relations += 1
                            logger.debug(f"🔄 追加关系: [{source}] --[{relation_type}]--> [{target}]")
                    else:
                        # 新关系，直接添加
                        self.graph.add_edge(
                            source,
                            target,
                            relation=relation_type,
                            description=relation.get('description', ''),
                            source_document=filename
                        )
                        added_relations += 1
                        logger.debug(f"➕ 新增关系: [{source}] --[{relation_type}]--> [{target}]")
                else:
                    # 记录缺失的实体
                    missing = []
                    if not source_exists:
                        missing.append(f"源实体'{source}'")
                    if not target_exists:
                        missing.append(f"目标实体'{target}'")
                    
                    skipped_relations.append({
                        'relation': relation_type,
                        'source': source,
                        'target': target,
                        'missing': ', '.join(missing)
                    })
                    logger.warning(f"⚠️ 跳过关系 [{source}] --[{relation_type}]--> [{target}]: {', '.join(missing)} 不存在")
            
            # 输出统计信息
            logger.info(f"✅ 关系处理完成: 新增 {added_relations} 条，更新 {updated_relations} 条，当前图中共有 {self.graph.number_of_edges()} 条边")
            if skipped_relations:
                logger.warning(f"⚠️ 跳过了 {len(skipped_relations)} 条关系（因为实体不存在）")
                # 输出前5个被跳过的关系作为示例
                for i, rel in enumerate(skipped_relations[:5]):
                    logger.warning(f"  示例 {i+1}: [{rel['source']}] --[{rel['relation']}]--> [{rel['target']}] (缺失: {rel['missing']})")
            
            result = {
                "success": True,
                "filename": filename,
                "new_entities": new_entities,
                "updated_entities": updated_entities,
                "entities_count": len(unique_entities),
                "new_relations": added_relations,
                "updated_relations": updated_relations,
                "relations_count": added_relations + updated_relations,
                "skipped_relations_count": len(skipped_relations),
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "message": f"成功构建知识图谱：新增 {new_entities} 个实体，更新 {updated_entities} 个实体；新增 {added_relations} 条关系，更新 {updated_relations} 条关系" + 
                          (f"（跳过了 {len(skipped_relations)} 条关系，因为实体不存在）" if skipped_relations else "")
            }
            
            # 如果有跳过的关系，添加到结果中供调试
            if skipped_relations:
                result["skipped_relations"] = skipped_relations[:10]  # 只返回前10个示例
            
            # 💾 保存到磁盘（持久化）
            save_success = self.save_graph()
            result["persisted"] = save_success
            
            logger.info(f"文档 {filename} 的知识图谱构建完成{'并已保存到磁盘' if save_success else '（保存失败）'}")
            return result
            
        except Exception as e:
            logger.error(f"构建知识图谱失败: {str(e)}")
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": f"构建知识图谱失败: {str(e)}"
            }
    
    def query_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        查询实体信息及其关系
        
        Args:
            entity_name: 实体名称
            
        Returns:
            实体信息和关系
        """
        try:
            if entity_name not in self.graph.nodes:
                return {
                    "success": False,
                    "message": f"未找到实体: {entity_name}"
                }
            
            # 获取实体属性
            entity_data = self.graph.nodes[entity_name]
            
            # 获取出边（该实体指向其他实体的关系）
            outgoing = []
            for target in self.graph.successors(entity_name):
                edge_data = self.graph.edges[entity_name, target]
                outgoing.append({
                    "target": target,
                    "relation": edge_data.get('relation', 'related_to'),
                    "description": edge_data.get('description', '')
                })
            
            # 获取入边（其他实体指向该实体的关系）
            incoming = []
            for source in self.graph.predecessors(entity_name):
                edge_data = self.graph.edges[source, entity_name]
                incoming.append({
                    "source": source,
                    "relation": edge_data.get('relation', 'related_to'),
                    "description": edge_data.get('description', '')
                })
            
            return {
                "success": True,
                "entity": {
                    "name": entity_name,
                    "type": entity_data.get('type', 'Unknown'),
                    "description": entity_data.get('description', ''),
                    "source_document": entity_data.get('source_document', '')
                },
                "outgoing_relations": outgoing,
                "incoming_relations": incoming,
                "relations_count": len(outgoing) + len(incoming)
            }
            
        except Exception as e:
            logger.error(f"查询实体失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def find_path(self, source: str, target: str, max_length: int = 5) -> Dict[str, Any]:
        """
        查找两个实体之间的关系路径
        
        Args:
            source: 源实体
            target: 目标实体
            max_length: 最大路径长度
            
        Returns:
            路径信息
        """
        try:
            if source not in self.graph.nodes:
                return {"success": False, "message": f"未找到实体: {source}"}
            
            if target not in self.graph.nodes:
                return {"success": False, "message": f"未找到实体: {target}"}
            
            # 查找最短路径
            try:
                path = nx.shortest_path(self.graph, source, target)
                
                # 构建路径描述
                path_description = []
                for i in range(len(path) - 1):
                    edge_data = self.graph.edges[path[i], path[i+1]]
                    path_description.append({
                        "from": path[i],
                        "to": path[i+1],
                        "relation": edge_data.get('relation', 'related_to')
                    })
                
                return {
                    "success": True,
                    "path": path,
                    "path_length": len(path) - 1,
                    "path_description": path_description
                }
                
            except nx.NetworkXNoPath:
                return {
                    "success": False,
                    "message": f"{source} 和 {target} 之间没有路径"
                }
            
        except Exception as e:
            logger.error(f"查找路径失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """
        获取知识图谱统计信息
        
        Returns:
            统计信息
        """
        try:
            # 统计实体类型分布
            entity_types_count = defaultdict(int)
            for node in self.graph.nodes:
                node_type = self.graph.nodes[node].get('type', 'Unknown')
                entity_types_count[node_type] += 1
            
            # 统计关系类型分布
            relation_types_count = defaultdict(int)
            for edge in self.graph.edges:
                relation_type = self.graph.edges[edge].get('relation', 'related_to')
                relation_types_count[relation_type] += 1
            
            return {
                "success": True,
                "total_entities": self.graph.number_of_nodes(),
                "total_relations": self.graph.number_of_edges(),
                "entity_types": dict(entity_types_count),
                "relation_types": dict(relation_types_count),
                "graph_density": nx.density(self.graph)
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_graph_data(self) -> Dict[str, Any]:
        """
        导出图数据用于前端可视化
        
        Returns:
            图数据（nodes和edges格式）
        """
        try:
            logger.info(f"开始导出图数据，当前图中有 {self.graph.number_of_nodes()} 个节点，{self.graph.number_of_edges()} 条边")
            
            nodes = []
            for node in self.graph.nodes:
                node_data = self.graph.nodes[node]
                nodes.append({
                    "id": node,
                    "label": node,
                    "type": node_data.get('type', 'Unknown'),
                    "description": node_data.get('description', ''),
                    "source_document": node_data.get('source_document', '')
                })
            
            edges = []
            for edge in self.graph.edges:
                edge_data = self.graph.edges[edge]
                edges.append({
                    "source": edge[0],
                    "target": edge[1],
                    "relation": edge_data.get('relation', 'related_to'),
                    "description": edge_data.get('description', '')
                })
            
            logger.info(f"导出完成：{len(nodes)} 个节点，{len(edges)} 条边")
            
            return {
                "success": True,
                "nodes": nodes,
                "edges": edges,
                "nodes_count": len(nodes),
                "edges_count": len(edges)
            }
            
        except Exception as e:
            logger.error(f"导出图数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_entities(self, keyword: str = "", entity_type: Optional[str] = None) -> Dict[str, Any]:
        """
        搜索包含关键词的实体
        
        Args:
            keyword: 搜索关键词（空字符串表示返回所有实体）
            entity_type: 实体类型过滤（可选）
            
        Returns:
            匹配的实体列表
        """
        try:
            matched_entities = []
            
            # 如果关键词为空，返回所有实体（可能很多，限制数量）
            is_all = not keyword or keyword.strip() == ""
            
            for node in self.graph.nodes:
                node_data = self.graph.nodes[node]
                
                # 类型过滤
                if entity_type and node_data.get('type') != entity_type:
                    continue
                
                # 关键词匹配（名称或描述）
                # 如果 keyword 为空，则匹配所有
                if is_all or (keyword.lower() in node.lower() or 
                    keyword.lower() in node_data.get('description', '').lower()):
                    matched_entities.append({
                        "name": node,
                        "type": node_data.get('type', 'Unknown'),
                        "description": node_data.get('description', ''),
                        "source_document": node_data.get('source_document', '')
                    })
                
                # 如果返回所有实体，限制最多返回 100 个（防止数据过大）
                if is_all and len(matched_entities) >= 100:
                    logger.warning(f"实体数量过多，限制返回前 100 个")
                    break
            
            return {
                "success": True,
                "keyword": keyword if keyword else "全部",
                "entity_type": entity_type,
                "results": matched_entities,
                "count": len(matched_entities),
                "is_limited": is_all and len(matched_entities) >= 100
            }
            
        except Exception as e:
            logger.error(f"搜索实体失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# 创建全局实例
knowledge_graph_tools = KnowledgeGraphTools()
