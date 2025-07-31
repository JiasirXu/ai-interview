#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封装讯飞Spark X1的HTTP + WebSocket调用
"""

import json
import re
import requests
import time
from typing import Dict, Any, List, Optional, Callable
from loguru import logger
from app.utils.ws_client import SparkWebSocketClient
from flask import current_app
import asyncio

class SparkService:
    """讯飞Spark服务"""
    
    def __init__(self, config=None):
        self.config = config
        self.spark_config = None
        self.http_url = None
        self.websocket_url = None
        self.api_password = None
        self.ws_client = None
        self.session_active = False
        self.conversation_history = []
        self._initialized = False
        self.conversation_history = []  # 对话历史
        self.response_callback = None
    
    def _ensure_initialized(self):
        """确保服务已初始化"""
        if not self._initialized:
            if self.config is None:
                from flask import current_app
                self.config = current_app.config.get('XUNFEI_CONFIG', {})
            
            self.spark_config = self.config.get('SPARK', {})
            self.http_url = self.spark_config.get('HTTP_URL')
            self.websocket_url = self.spark_config.get('WEBSOCKET_URL')
            self.api_password = self.spark_config.get('HTTP_PASSWORD')
            self._initialized = True
    
    def set_response_callback(self, callback: Callable[[str], None]):
        """设置流式响应回调函数"""
        self.response_callback = callback

    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证headers"""
        self._ensure_initialized()
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_password}"
        }
    
    def chat_completion_http(self, messages: List[Dict[str, str]], system_prompt: str = None, max_retries: int = 3) -> Dict[str, Any]:
        """
        HTTP方式调用Spark聊天完成（带重试机制）

        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词
            max_retries: 最大重试次数

        Returns:
            API响应结果
        """
        self._ensure_initialized()

        last_error = None

        for attempt in range(max_retries):
            try:
                # 构建请求payload
                payload = {
                    "model": "x1",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": False
                }

                # 如果有系统提示词，添加到消息开头
                if system_prompt:
                    payload["messages"].insert(0, {
                        "role": "system",
                        "content": system_prompt
                    })

                # 动态调整超时时间（每次重试增加30秒）
                timeout = 180 + (attempt * 30)

                logger.info(f"发送Spark HTTP请求 (尝试 {attempt + 1}/{max_retries}): {len(messages)}条消息, 超时时间: {timeout}秒")

                # 发送HTTP请求
                response = requests.post(
                    self.http_url,
                    headers=self._get_auth_headers(),
                    json=payload,
                    timeout=timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Spark HTTP调用成功 (尝试 {attempt + 1}/{max_retries})")
                    return {
                        'success': True,
                        'data': result,
                        'message': result.get('choices', [{}])[0].get('message', {}).get('content', ''),
                        'attempts': attempt + 1
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"Spark HTTP调用失败 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                    last_error = error_msg

                    # 如果是最后一次尝试，返回错误
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'error': last_error,
                            'attempts': max_retries
                        }

                    # 等待一段时间后重试（指数退避）
                    import time
                    wait_time = 2 ** attempt  # 1, 2, 4 秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Spark HTTP调用异常 (尝试 {attempt + 1}/{max_retries}): {error_msg}")
                last_error = error_msg

                # 如果是最后一次尝试，返回错误
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'error': last_error,
                        'attempts': max_retries
                    }

                # 等待一段时间后重试
                import time
                wait_time = 2 ** attempt
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

        # 理论上不会到达这里，但为了安全起见
        return {
            'success': False,
            'error': last_error or 'Unknown error',
            'attempts': max_retries
        }

    def analyze_resume(self, resume_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        分析简历内容，提取技能和岗位匹配

        Args:
            resume_text: 简历文本内容
            max_retries: 最大重试次数

        Returns:
            分析结果
        """
        system_prompt = """
        你是一个专业的简历分析专家。请仔细分析以下简历内容，准确提取关键信息：

        **重要提醒：请仔细阅读简历原文，不要遗漏任何技能、工作经历和项目信息！**

        **提取要求：**
        1. **技能标签**：从简历中提取所有技术技能，包括：
           - 编程语言：如Java、C/C++、JavaScript、Python等
           - 开发工具：如Eclipse、Studio、Visual Studio等
           - 技术框架：如Spring、Vue.js、React等
           - 数据库：如MySQL、Oracle、MongoDB等
           - 网络技术：如TCP、UDP、HTTP等
           - 其他技术：如ASP、DELPHI、AIDL、Messenger等
           - 注意：要提取简历中明确提到的所有技术名称，不要遗漏

        2. **工作经历和项目经历**：提取所有工作经历、实习经历和项目经历，包括：
           - 工作经历（WORK EXPERIENCE）：公司职位、工作内容、时间段
           - 实习经历：实习公司、实习职位、实习内容
           - 项目经历：学校项目、个人项目、工作项目
           - 实践经历：各种实践活动

           **特别注意**：
           - 如果简历中有"工作经历"、"WORK EXPERIENCE"等标题，请重点提取
           - 每个经历都要包含：title（职位/项目名）、description（工作内容/项目描述）、technologies（相关技术）、period（时间段）、company（公司名称，如果有）

        3. **岗位推荐**：基于识别出的技能和经历推荐匹配岗位
        4. **工作年限**：根据工作经历和实习经历估算总工作年限
        5. **优势总结**：总结核心技能优势和工作经验优势

        **返回JSON格式：**
        {
          "skills": ["技能1", "技能2", "技能3"],
          "projects": [
            {
              "title": "职位名称或项目名称",
              "description": "工作内容或项目描述",
              "technologies": ["相关技术"],
              "period": "时间段",
              "company": "公司名称（如果是工作经历）"
            }
          ],
          "positions": ["推荐岗位1", "推荐岗位2"],
          "experience_years": 工作年限数字,
          "strengths": "优势总结"
        }
        """
        
        messages = [
            {
                "role": "user",
                "content": f"请分析以下简历内容：\n\n{resume_text}"
            }
        ]
        
        logger.info(f"发送给AI的简历文本长度: {len(resume_text)}")
        logger.debug(f"简历文本前500字符: {resume_text[:500]}")

        result = self.chat_completion_http(messages, system_prompt, max_retries)

        if result['success']:
            try:
                # 尝试解析JSON结果
                content = result['message']
                logger.info(f"AI返回的原始内容长度: {len(content)}")
                logger.debug(f"AI返回的原始内容: {content}")

                # 提取JSON部分（如果有其他文本）
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    logger.debug(f"提取的JSON字符串: {json_str}")
                    analysis = json.loads(json_str)
                    logger.info(f"解析成功，技能数量: {len(analysis.get('skills', []))}")
                    logger.info(f"解析的技能列表: {analysis.get('skills', [])}")
                    return {
                        'success': True,
                        'analysis': analysis
                    }
                else:
                    # 如果AI没有返回json，而是普通文本，也将其作为strengths返回
                    logger.warning("AI未返回标准JSON格式的简历分析，将直接使用文本内容。")
                    logger.debug(f"非JSON内容: {content}")
                    return {
                        'success': True,
                        'analysis': {'strengths': content}
                    }
            except Exception as e:
                logger.error(f"解析简历分析结果失败: {e}")
                return {
                    'success': False,
                    'error': f'解析结果失败: {str(e)}'
                }
        else:
            return result
    
    def _build_interview_system_prompt(self, interview_config: Dict[str, Any]) -> str:
        """
        根据面试配置构建个性化的system_prompt

        Args:
            interview_config: 面试配置，包含模式、难度、岗位等信息

        Returns:
            个性化的system_prompt
        """
        interview_mode = interview_config.get('interview_mode', 'technical')
        difficulty_level = interview_config.get('difficulty_level', 'middle')
        position = interview_config.get('position', '软件工程师')
        interaction_mode = interview_config.get('interaction_mode', 'frequent')

        # 基础角色设定
        base_prompt = "你是一个专业的AI面试官。"

        # 根据面试模式调整角色
        mode_prompts = {
            'technical': f"你专注于考察候选人的技术能力和编程技能，特别是{position}相关的技术栈。",
            'behavioral': "你专注于考察候选人的软技能、工作经验和行为表现，通过STAR模型来评估。",
            'case': "你通过实际案例和场景问题来考察候选人的分析能力、解决问题的思路和实践经验。",
            'comprehensive': f"你会从技术能力、行为表现、项目经验等多个维度全面考察{position}候选人。"
        }

        # 根据难度级别调整问题深度
        difficulty_prompts = {
            'primary': "问题应该适合应届生和初级开发者，重点考察基础概念和学习能力。",
            'middle': "问题应该适合有1-3年经验的开发者，考察实际项目经验和技术深度。",
            'high': "问题应该适合资深开发者和技术专家，考察架构设计、技术领导力和复杂问题解决能力。"
        }

        # 根据互动模式调整提问风格
        interaction_prompts = {
            'frequent': "你会问很多细节问题和追问，保持高频互动，深入挖掘候选人的能力。",
            'listener': "你会问较少但深入的问题，给候选人充分的表达时间，仔细倾听并适时引导。",
            'counter': "你会针对候选人的回答进行反问和质疑，考察其思维逻辑和应变能力。"
        }

        # 组合完整的prompt
        full_prompt = f"""
        {base_prompt}

        【面试模式】{mode_prompts.get(interview_mode, mode_prompts['technical'])}

        【难度级别】{difficulty_prompts.get(difficulty_level, difficulty_prompts['middle'])}

        【互动风格】{interaction_prompts.get(interaction_mode, interaction_prompts['frequent'])}

        【评估要求】
        - 根据候选人的回答给出实时反馈和建议
        - 评估技术深度、表达逻辑、项目经验等维度
        - 保持专业、友好的面试氛围
        - 适时给出鼓励和改进建议

        请根据以上要求进行面试，确保问题质量和面试体验。
        """

        return full_prompt.strip()

    def _get_position_focus(self, position: str) -> str:
        """
        根据岗位获取面试重点

        Args:
            position: 岗位代码

        Returns:
            岗位面试重点描述
        """
        position_focuses = {
            # AI方向
            'ai_algorithm_engineer': '重点考察机器学习算法、深度学习框架使用、模型优化和数学基础',
            'machine_learning_engineer': '重点考察ML工程实践、模型部署、数据处理和系统架构能力',
            'ai_product_manager': '重点考察AI产品规划、技术理解、用户需求分析和项目管理能力',
            'ai_data_scientist': '重点考察数据分析、统计学基础、业务理解和数据挖掘技能',

            # 大数据方向
            'big_data_engineer': '重点考察大数据技术栈、分布式系统、数据处理和性能优化',
            'data_analyst': '重点考察数据分析方法、可视化技能、业务洞察和统计分析能力',
            'data_product_manager': '重点考察数据产品设计、指标体系、用户画像和商业分析',
            'data_architect': '重点考察数据架构设计、技术选型、系统规划和团队协作',

            # 物联网方向
            'iot_engineer': '重点考察物联网协议、嵌入式开发、传感器技术和系统集成',
            'embedded_engineer': '重点考察嵌入式系统、硬件接口、实时系统和底层编程',
            'iot_product_manager': '重点考察物联网产品规划、技术理解、市场分析和生态建设',
            'iot_solution_architect': '重点考察物联网架构设计、技术选型、安全方案和项目实施'
        }

        return position_focuses.get(position, '重点考察专业技能、项目经验和综合素质')

    def add_to_conversation(self, role: str, content: str):
        """
        添加对话到历史记录

        Args:
            role: 角色 ('user' 或 'assistant')
            content: 对话内容
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })

        # 限制历史记录长度，避免token过多
        if len(self.conversation_history) > 20:
            # 保留最近的20条对话
            self.conversation_history = self.conversation_history[-20:]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史

        Returns:
            对话历史列表
        """
        return self.conversation_history.copy()

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def _build_evaluation_system_prompt(self, interview_config: Dict[str, Any], interview_preferences: Dict[str, Any]) -> str:
        """
        构建个性化的评估system_prompt

        Args:
            interview_config: 面试配置
            interview_preferences: 面试偏好设置

        Returns:
            评估system_prompt
        """
        interview_mode = interview_config.get('interview_mode', 'technical')
        difficulty_level = interview_config.get('difficulty_level', 'middle')
        position = interview_config.get('position', '软件工程师')

        base_prompt = "你是一个专业的面试评估专家。"

        # 根据面试模式调整评估重点
        mode_evaluation_focus = {
            'technical': f"重点评估候选人的技术能力、编程技能和{position}相关的专业知识。",
            'behavioral': "重点评估候选人的软技能、工作经验、团队协作能力和行为表现。",
            'case': "重点评估候选人的分析能力、解决问题的思路、逻辑思维和实践应用能力。",
            'comprehensive': f"从技术能力、行为表现、项目经验等多个维度全面评估{position}候选人。"
        }

        # 根据难度级别调整评估标准
        difficulty_standards = {
            'primary': "评估标准适合应届生和初级开发者，重点关注基础知识掌握和学习潜力。",
            'middle': "评估标准适合有1-3年经验的开发者，重点关注实际项目经验和技术深度。",
            'high': "评估标准适合资深开发者和技术专家，重点关注架构设计、技术领导力和复杂问题解决能力。"
        }

        evaluation_prompt = f"""
        {base_prompt}

        【评估重点】{mode_evaluation_focus.get(interview_mode, mode_evaluation_focus['technical'])}

        【评估标准】{difficulty_standards.get(difficulty_level, difficulty_standards['middle'])}

        【评估要求】
        - 根据面试对话内容进行客观、公正的评估
        - 评分应该基于候选人的实际表现和回答质量
        - 提供具体的优势分析和改进建议
        - 评估结果应该对候选人的职业发展有指导意义
        - 考虑目标岗位的具体要求和行业标准

        请确保评估结果专业、准确、有建设性。
        """

        return evaluation_prompt.strip()

    def _build_conversation_summary(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        构建对话历史摘要

        Args:
            conversation_history: 对话历史

        Returns:
            对话摘要
        """
        if not conversation_history:
            return "无对话记录"

        summary_parts = []
        question_count = 0

        for entry in conversation_history:
            role = entry.get('role', 'unknown')
            content = entry.get('content', '')

            if role == 'assistant' and content:  # 面试官的问题
                question_count += 1
                summary_parts.append(f"问题{question_count}: {content[:100]}...")

            elif role == 'user' and content:  # 候选人的回答
                summary_parts.append(f"回答{question_count}: {content[:200]}...")

        if not summary_parts:
            return "对话记录为空或格式异常"

        summary = "\n".join(summary_parts)
        return f"总共进行了{question_count}轮问答：\n{summary}"

    def generate_interview_questions(self, resume_analysis: Dict[str, Any], position: str) -> Dict[str, Any]:
        """
        根据简历分析结果生成面试问题
        
        Args:
            resume_analysis: 简历分析结果
            position: 目标岗位
            
        Returns:
            面试问题列表
        """
        system_prompt = f"""
        你是一个专业的面试官。根据候选人的简历分析结果和目标岗位"{position}"，
        生成3-5个面试问题。请以JSON格式返回，包含一个名为'questions'的数组，
        数组中每个对象都应包含三个字段：
        1. 'type': 问题类型（例如：'技术', '项目', '行为'）
        2. 'content': 问题内容（字符串）
        3. 'reference_answer': 针对该问题的专业参考答案（字符串，至少50字）
        """
        
        messages = [
            {
                "role": "user",
                "content": f"简历分析结果：{json.dumps(resume_analysis, ensure_ascii=False)}"
            }
        ]
        
        result = self.chat_completion_http(messages, system_prompt)
        
        if result['success']:
            try:
                content = result['message']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    # 验证返回的数据结构
                    if 'questions' in parsed_data and isinstance(parsed_data['questions'], list):
                        return {
                            'success': True,
                            'data': parsed_data
                        }
                    else:
                        raise ValueError("返回的JSON缺少 'questions' 数组")
                else:
                    raise ValueError("AI未返回JSON格式")
            except Exception as e:
                logger.error(f"解析面试问题JSON失败: {e}")
                return {'success': False, 'error': f"解析AI响应失败: {e}"}
        else:
            return result

    def generate_personalized_first_question(self, resume_analysis: Dict[str, Any], interview_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据简历分析和面试配置生成个性化的首问

        Args:
            resume_analysis: 简历分析结果
            interview_config: 面试配置

        Returns:
            个性化的首问
        """
        # 构建个性化的system_prompt
        system_prompt = self._build_interview_system_prompt(interview_config)

        # 根据岗位类型调整首问重点
        position = interview_config.get('position', '软件工程师')
        position_focus = self._get_position_focus(position)

        # 添加首问生成的具体要求
        system_prompt += f"""

        【首问生成要求】
        目标岗位：{position}
        岗位重点：{position_focus}

        现在请根据候选人的简历分析结果和目标岗位要求，生成一个合适的开场问题。
        请以JSON格式返回，包含一个名为'questions'的数组，数组中包含一个问题对象，
        该对象应包含三个字段：
        1. 'type': 问题类型（例如：'开场', '自我介绍', '项目经验'）
        2. 'content': 问题内容（字符串，应该是一个友好的开场问题）
        3. 'reference_answer': 针对该问题的专业参考答案（字符串，至少50字）

        开场问题应该：
        - 让候选人感到轻松和舒适
        - 与其简历背景和目标岗位相关
        - 为后续深入交流做好铺垫
        - 体现出你对其简历和岗位要求的了解
        - 针对{position}岗位的特点进行提问
        """

        messages = [
            {
                "role": "user",
                "content": f"候选人简历分析结果：{json.dumps(resume_analysis, ensure_ascii=False)}\n\n目标岗位：{interview_config.get('position', '软件工程师')}\n\n目标公司：{interview_config.get('company', '知名互联网公司')}"
            }
        ]

        result = self.chat_completion_http(messages, system_prompt)

        if result['success']:
            try:
                content = result['message']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    # 验证返回的数据结构
                    if 'questions' in parsed_data and isinstance(parsed_data['questions'], list):
                        return {
                            'success': True,
                            'data': parsed_data
                        }
                    else:
                        raise ValueError("返回的JSON缺少 'questions' 数组")
                else:
                    raise ValueError("AI未返回JSON格式")
            except Exception as e:
                logger.error(f"解析个性化首问JSON失败: {e}")
                return {'success': False, 'error': f"解析AI响应失败: {e}"}
        else:
            return result

    async def generate_next_question_based_on_history(self, interview_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """根据对话历史生成下一个问题和参考答案"""
        system_prompt = self._build_interview_system_prompt(interview_config or {})
        messages = self.get_conversation_history()
        messages.append({"role": "system", "content": "基于当前对话历史，生成下一个合适的问题及其参考答案。输出格式：{'question': '问题文本', 'reference_answer': '参考答案'}"})
        result = self.chat_completion_http(messages, system_prompt)
        if result['success']:
            try:
                data = json.loads(result['message'])
                return {'success': True, 'data': data}
            except:
                return {'success': False, 'error': '解析失败'}
        return result

    async def start_websocket_session(self, system_prompt: str = None, interview_config: Dict[str, Any] = None) -> bool:
        """
        启动WebSocket会话

        Args:
            system_prompt: 系统提示词（如果提供，将覆盖interview_config生成的prompt）
            interview_config: 面试配置，用于生成个性化的system_prompt

        Returns:
            是否启动成功
        """
        # 如果没有提供system_prompt但有interview_config，则生成个性化prompt
        if not system_prompt and interview_config:
            system_prompt = self._build_interview_system_prompt(interview_config)
        elif not system_prompt:
            system_prompt = "你是一个专业的AI面试官。你将收到包含用户文本、情感和是否为最终句的JSON。请根据这些信息，实时地、流式地给出你的分析和反馈。"
        self._ensure_initialized()
        try:
            # 传递spark_config，而不是整个config，使依赖更清晰
            self.ws_client = SparkWebSocketClient(self.spark_config)
            success = await self.ws_client.start_conversation(system_prompt)
            
            if success:
                self.session_active = True
                self.conversation_history = []
                logger.info("Spark WebSocket会话启动成功")
                # 启动后台任务以持续接收消息
                asyncio.create_task(self.receive_ai_responses_continuously())
            
            return success
        except Exception as e:
            logger.error(f"启动WebSocket会话失败: {e}")
            return False
    
    async def send_user_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        发送结构化的用户反馈到WebSocket
        
        Args:
            feedback_data: 包含用户回答文本和情感数据的字典
            
        Returns:
            是否发送成功
        """
        if not self.session_active or not self.ws_client:
            logger.error("WebSocket会话未激活")
            return False
        
        try:
            # 添加到对话历史
            self.conversation_history.append({
                'role': 'user',
                'content': json.dumps(feedback_data, ensure_ascii=False),
                'timestamp': time.time()
            })
            
            # 将结构化数据发送到WebSocket
            # Spark V2 ws接口的text字段是一个数组
            payload_text = [{"role": "user", "content": json.dumps(feedback_data, ensure_ascii=False)}]
            return await self.ws_client.send_user_message(payload_text)
        except Exception as e:
            logger.error(f"发送用户反馈失败: {e}")
            return False
    
    async def receive_ai_responses_continuously(self):
        """持续接收AI响应并调用回调"""
        while self.session_active and self.ws_client:
            try:
                response = await self.ws_client.receive_message()
                if response:
                    # 将响应添加到对话历史
                    content = response.get('payload', {}).get('choices', {}).get('text', [{}])[0].get('content', '')
                    self.conversation_history.append({
                        'role': 'assistant',
                        'content': content,
                        'timestamp': time.time()
                    })

                    # 如果设置了回调，则调用它
                    if self.response_callback and content:
                        try:
                            self.response_callback(content)
                        except Exception as cb_e:
                            logger.error(f"执行AI响应回调函数失败: {cb_e}")
                    
                    # 检查对话是否结束
                    status = response.get('header', {}).get('status')
                    if status == 2:
                        logger.info("Spark会话已由服务器端关闭。")
                        await self.end_websocket_session()
                        break
                else:
                    # 如果返回None，可能表示连接已关闭
                    logger.warning("从Spark WebSocket接收到None，可能连接已关闭。")
                    await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                logger.info("接收AI响应任务被取消。")
                break
            except Exception as e:
                logger.error(f"接收AI响应时出错: {e}")
                # 避免因错误而快速循环
                await asyncio.sleep(1)
        logger.info("AI响应接收循环结束。")

    async def receive_ai_response(self) -> Optional[Dict[str, Any]]:
        """
        接收AI响应
        
        Returns:
            AI响应数据
        """
        if not self.session_active or not self.ws_client:
            return None
        
        try:
            response = await self.ws_client.receive_message()
            if response:
                # 添加到对话历史
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response.get('content', ''),
                    'feedback': response.get('feedback', {}),
                    'timestamp': time.time()
                })
            
            return response
        except Exception as e:
            logger.error(f"接收AI响应失败: {e}")
            return None
    
    async def end_websocket_session(self) -> bool:
        """
        结束WebSocket会话
        
        Returns:
            是否结束成功
        """
        try:
            if self.ws_client:
                # 停止持续接收任务（如果它在运行）
                tasks = [t for t in asyncio.all_tasks() if t.get_coro().__name__ == 'receive_ai_responses_continuously']
                for task in tasks:
                    task.cancel()

                await self.ws_client.end_conversation()
                self.ws_client = None
            
            self.session_active = False
            logger.info("Spark WebSocket会话已结束")
            return True
        except Exception as e:
            logger.error(f"结束WebSocket会话失败: {e}")
            return False
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()
    
    def generate_personalized_final_evaluation(self,
                                             conversation_history: List[Dict[str, Any]],
                                             interview_config: Dict[str, Any],
                                             interview_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成个性化的最终面试评估

        Args:
            conversation_history: 对话历史
            interview_config: 面试配置
            interview_preferences: 面试偏好设置

        Returns:
            个性化评估结果
        """
        # 构建个性化的评估system_prompt
        evaluation_prompt = self._build_evaluation_system_prompt(interview_config, interview_preferences)

        # 构建对话历史摘要
        conversation_summary = self._build_conversation_summary(conversation_history)

        messages = [
            {
                "role": "user",
                "content": f"""
                请根据以下面试对话历史，生成详细的面试评估报告。

                面试配置信息：
                - 面试模式：{interview_config.get('interview_mode', '技术面试')}
                - 难度级别：{interview_config.get('difficulty_level', '中级')}
                - 目标岗位：{interview_config.get('position', '软件工程师')}
                - 目标公司：{interview_config.get('company', '知名互联网公司')}
                - 互动模式：{interview_config.get('interaction_mode', '高频询问型')}

                对话历史摘要：
                {conversation_summary}

                请以JSON格式返回评估结果，包含以下字段：
                - 综合评分 (0-100)
                - 技术能力评分 (0-100)
                - 表达逻辑评分 (0-100)
                - 应变能力评分 (0-100)
                - 行为礼仪评分 (0-100)
                - 文化匹配评分 (0-100)
                - 详细评价 (字符串)
                - 优势分析 (数组)
                - 改进建议 (数组)
                - 岗位匹配度 (0-100)
                """
            }
        ]

        result = self.chat_completion_http(messages, evaluation_prompt)

        if result['success']:
            try:
                content = result['message']
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return {
                        'success': True,
                        'data': {
                            'message': content,
                            'evaluation': parsed_data
                        }
                    }
                else:
                    raise ValueError("AI未返回JSON格式")
            except Exception as e:
                logger.error(f"解析个性化评估JSON失败: {e}")
                return {'success': False, 'error': f"解析AI响应失败: {e}"}
        else:
            return result

    def generate_final_evaluation(self, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成最终面试评估
        
        Args:
            conversation_history: 对话历史
            
        Returns:
            评估结果
        """
        system_prompt = """
        你是一个专业的面试评估专家。根据面试对话历史，提供综合评估：
        1. 技术能力评分（1-10）
        2. 沟通能力评分（1-10）
        3. 项目经验评分（1-10）
        4. 综合评分（1-10）
        5. 优势分析
        6. 改进建议
        
        请以JSON格式返回结果。
        """
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history
        ])
        
        messages = [
            {
                "role": "user",
                "content": f"面试对话记录：\n\n{conversation_text}"
            }
        ]
        
        return self.chat_completion_http(messages, system_prompt)


# 全局服务实例
spark_service = SparkService()