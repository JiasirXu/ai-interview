#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简历内容分析器
"""

import re
from datetime import datetime
from loguru import logger

class ResumeAnalyzer:
    """简历内容分析器"""
    
    # 扩展的技能关键词库
    SKILL_KEYWORDS = {
        'programming_languages': [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'PHP', 'Ruby', 'Swift', 'Kotlin', 'Dart', 'Scala', 'R', 'MATLAB', 'C',
            'C语言', 'Objective-C', 'Perl', 'Shell', 'PowerShell', 'Lua', 'ASP',
            'DELPHI', 'Delphi', 'VB', 'Visual Basic', 'Haskell', 'Erlang', 'Elixir',
            'F#', 'Clojure', 'Julia', 'Groovy', 'Assembly', '汇编', 'COBOL', 'Fortran'
        ],
        'frontend': [
            'Vue.js', 'Vue', 'React', 'Angular', 'jQuery', 'Bootstrap', 'Tailwind CSS',
            'HTML', 'HTML5', 'CSS', 'CSS3', 'SCSS', 'SASS', 'Less', 'Webpack', 'Vite',
            'Element UI', 'Ant Design', 'Vuetify', 'Quasar', 'Nuxt.js', 'Next.js',
            'Gatsby', 'Svelte', 'Alpine.js', 'Stimulus', 'Ember.js', 'Backbone.js',
            'Meteor', 'Ionic', 'React Native', 'Flutter', 'Electron', 'Cordova',
            'Uni-app', '微信小程序', '支付宝小程序', 'Taro', 'Wepy'
        ],
        'backend': [
            'Node.js', 'Express', 'Koa', 'Nest.js', 'Spring', 'Spring Boot', 'Django',
            'Flask', 'FastAPI', 'Laravel', 'CodeIgniter', 'ASP.NET', 'Gin', 'Echo',
            'Spring Cloud', 'MyBatis', 'Hibernate', 'JPA', 'Struts', 'Rails',
            'Tornado', 'Celery', 'Gunicorn', 'uWSGI', 'Dubbo', 'Netty', 'Vert.x',
            'Quarkus', 'Micronaut', 'Akka', 'Play Framework', 'Grails', 'Sinatra'
        ],
        'database': [
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle',
            'SQL Server', 'Elasticsearch', 'InfluxDB', 'Cassandra', 'MariaDB',
            'DynamoDB', 'Neo4j', 'CouchDB', 'HBase', 'ClickHouse', 'TiDB',
            'OceanBase', 'PolarDB', 'GaussDB', 'Memcached', 'RocksDB', 'LevelDB'
        ],
        'cloud_devops': [
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Google Cloud', 'Nginx',
            'Apache', 'Jenkins', 'GitLab CI', 'GitHub Actions', 'Terraform',
            'Ansible', 'Puppet', 'Chef', 'Vagrant', 'Consul', 'Vault', 'Prometheus',
            '阿里云', '腾讯云', '华为云', '百度云', 'OpenStack', 'CloudFoundry'
        ],
        'ai_ml': [
            'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy',
            'OpenCV', 'NLTK', 'SpaCy', 'Transformers', 'Hugging Face', 'LangChain',
            'Jupyter', 'Matplotlib', 'Seaborn', 'Plotly', 'XGBoost', 'LightGBM',
            'CatBoost', 'BERT', 'GPT', 'YOLO', 'ResNet', 'CNN', 'RNN', 'LSTM'
        ],
        'mobile': [
            'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
            'Cordova', 'Unity', 'Cocos2d', 'Kotlin', 'Swift', 'Objective-C',
            'Java', 'Dart', 'C#', 'Unity3D', 'Unreal Engine'
        ],
        'tools': [
            'Git', 'SVN', 'Linux', 'Ubuntu', 'CentOS', 'VS Code', 'IntelliJ IDEA',
            'Postman', 'Swagger', 'Jira', 'Confluence', 'Figma', 'Photoshop',
            'Eclipse', 'PyCharm', 'WebStorm', 'Android Studio', 'Xcode',
            'Vim', 'Emacs', 'Sublime Text', 'Atom', 'Notion', 'Slack', 'Teams'
        ]
    }

    # 岗位推荐关键词映射
    POSITION_KEYWORDS = {
        'Python开发工程师': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
        'Java开发工程师': ['java', 'spring', 'spring boot', 'mybatis', 'hibernate'],
        '前端开发工程师': ['javascript', 'vue', 'react', 'angular', 'html', 'css'],
        '全栈开发工程师': ['javascript', 'node.js', 'vue', 'react', 'python', 'java'],
        '移动端开发工程师': ['android', 'ios', 'react native', 'flutter', 'kotlin', 'swift'],
        '数据分析师': ['python', 'r', 'pandas', 'numpy', 'matplotlib', 'sql'],
        '算法工程师': ['python', 'tensorflow', 'pytorch', 'machine learning', 'deep learning'],
        'DevOps工程师': ['docker', 'kubernetes', 'jenkins', 'linux', 'aws', 'azure'],
        '测试工程师': ['selenium', 'junit', 'testng', 'postman', 'jmeter'],
        '产品经理': ['axure', 'figma', 'sketch', 'prototype', 'user experience']
    }
    
    @classmethod
    def extract_skills(cls, text):
        """
        从文本中提取技能
        
        Args:
            text (str): 简历文本内容
            
        Returns:
            list: 提取的技能列表
        """
        try:
            found_skills = []
            text_lower = text.lower()

            logger.debug(f"简历文本前500字符: {text[:500]}")

            # 遍历所有技能类别
            for category, skills in cls.SKILL_KEYWORDS.items():
                category_found = []
                for skill in skills:
                    # 使用正则表达式进行更精确的匹配
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    if re.search(pattern, text_lower):
                        found_skills.append(skill)
                        category_found.append(skill)

                if category_found:
                    logger.debug(f"在{category}类别中找到技能: {category_found}")

            # 去重并排序（忽略大小写）
            unique_skills = []
            seen_skills = set()
            for skill in found_skills:
                skill_lower = skill.lower()
                if skill_lower not in seen_skills:
                    unique_skills.append(skill)
                    seen_skills.add(skill_lower)
            unique_skills.sort()

            logger.info(f"提取到技能: {unique_skills}")
            return unique_skills
            
        except Exception as e:
            logger.error(f"技能提取失败: {e}")
            return []
    
    @classmethod
    def extract_projects(cls, text):
        """
        从文本中提取项目经历
        
        Args:
            text (str): 简历文本内容
            
        Returns:
            list: 提取的项目列表
        """
        try:
            projects = []
            
            # 项目匹配模式
            patterns = [
                # 匹配 "项目名称：xxx" 或 "项目：xxx"
                r'项目[名称：:\s]*([^\n\r]{10,100})',
                # 匹配 "Project: xxx" 或 "Project Name: xxx"
                r'[Pp]roject[\s\w]*[:：]\s*([^\n\r]{10,100})',
                # 匹配时间段 + 项目描述
                r'(\d{4}[.\-/年]\d{1,2}[.\-/月]?\d{0,2}[日]?[\s~\-至到]+\d{4}[.\-/年]\d{1,2}[.\-/月]?\d{0,2}[日]?)[\s\n\r]*([^\n\r]{20,200})',
                # 匹配项目描述段落
                r'(?:负责|参与|开发|设计|实现|完成)([^\n\r。！？]{30,200})',
            ]
            
            project_id = 1
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
                
                for match in matches:
                    if len(match.groups()) == 1:
                        # 单个匹配组（项目名称或描述）
                        content = match.group(1).strip()
                        
                        if cls._is_valid_project_content(content):
                            projects.append({
                                'id': project_id,
                                'title': content[:50] + ('...' if len(content) > 50 else ''),
                                'period': '时间不详',
                                'description': content
                            })
                            project_id += 1
                            
                    elif len(match.groups()) == 2:
                        # 两个匹配组（时间 + 描述）
                        period = match.group(1).strip()
                        description = match.group(2).strip()
                        
                        if cls._is_valid_project_content(description):
                            projects.append({
                                'id': project_id,
                                'title': description[:50] + ('...' if len(description) > 50 else ''),
                                'period': period,
                                'description': description
                            })
                            project_id += 1
            
            # 去重（基于描述内容）
            unique_projects = []
            seen_descriptions = set()
            
            for project in projects:
                desc_key = project['description'][:100]  # 使用前100个字符作为去重键
                if desc_key not in seen_descriptions:
                    seen_descriptions.add(desc_key)
                    unique_projects.append(project)
            
            # 限制项目数量
            result_projects = unique_projects[:5]
            
            logger.info(f"提取到项目: {len(result_projects)}个")
            return result_projects
            
        except Exception as e:
            logger.error(f"项目提取失败: {e}")
            return []
    
    @staticmethod
    def _is_valid_project_content(content):
        """
        验证项目内容是否有效
        
        Args:
            content (str): 项目内容
            
        Returns:
            bool: 是否有效
        """
        if not content or len(content.strip()) < 10:
            return False
        
        # 过滤掉一些无效内容
        invalid_patterns = [
            r'^[\d\s\-\.]+$',  # 纯数字和符号
            r'^[a-zA-Z\s]+$',  # 纯英文字母
            r'^\W+$',  # 纯特殊字符
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, content.strip()):
                return False
        
        return True
    
    @classmethod
    def extract_personal_info(cls, text):
        """
        提取个人信息

        Args:
            text (str): 简历文本内容

        Returns:
            dict: 个人信息
        """
        try:
            info = {}

            # 提取姓名（通常在简历开头）
            name_patterns = [
                r'姓\s*名[：:\s]*([^\n\r]{2,10})',
                r'Name[：:\s]*([^\n\r]{2,20})',
                r'^([^\n\r]{2,10})\s*简历',
                r'我是([^\n\r]{2,10})',
            ]

            for pattern in name_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    info['name'] = match.group(1).strip()
                    break

            # 提取电话
            phone_match = re.search(r'1[3-9]\d{9}', text)
            if phone_match:
                info['phone'] = phone_match.group()

            # 提取邮箱
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            if email_match:
                info['email'] = email_match.group()

            # 提取年龄
            age_patterns = [
                r'年龄[：:\s]*(\d{1,2})',
                r'Age[：:\s]*(\d{1,2})',
                r'(\d{1,2})岁',
            ]

            for pattern in age_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    age = int(match.group(1))
                    if 18 <= age <= 65:  # 合理年龄范围
                        info['age'] = age
                        break

            return info

        except Exception as e:
            logger.error(f"个人信息提取失败: {e}")
            return {}

    @classmethod
    def extract_education(cls, text):
        """
        提取教育背景

        Args:
            text (str): 简历文本内容

        Returns:
            list: 教育背景列表
        """
        try:
            education_list = []

            # 教育背景匹配模式
            patterns = [
                # 时间 + 学校 + 专业
                r'(\d{4}[.\-/年]\d{1,2}[.\-/月]?[\s~\-至到]+\d{4}[.\-/年]\d{1,2}[.\-/月]?)[\s\n\r]*([^\n\r]*(?:大学|学院|学校|University|College)[^\n\r]*?)[\s\n\r]*([^\n\r]*专业[^\n\r]*)',
                # 学校 + 专业 + 学历
                r'([^\n\r]*(?:大学|学院|University|College)[^\n\r]*?)[\s\n\r]*([^\n\r]*专业[^\n\r]*?)[\s\n\r]*([^\n\r]*(?:本科|硕士|博士|学士|硕士研究生|博士研究生|Bachelor|Master|PhD)[^\n\r]*)',
                # 简单的学校匹配
                r'([^\n\r]*(?:大学|学院|University|College)[^\n\r]{0,50})',
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 1:
                        education_info = {
                            'school': groups[0].strip() if len(groups) > 0 else '',
                            'major': groups[1].strip() if len(groups) > 1 else '',
                            'degree': groups[2].strip() if len(groups) > 2 else '',
                            'period': groups[0].strip() if len(groups) == 3 and '年' in groups[0] else ''
                        }

                        # 调整字段顺序（如果第一个字段包含年份，说明是时间）
                        if '年' in education_info['school'] or re.search(r'\d{4}', education_info['school']):
                            education_info = {
                                'period': education_info['school'],
                                'school': education_info['major'],
                                'major': education_info['degree'],
                                'degree': ''
                            }

                        if education_info['school'] and len(education_info['school']) > 2:
                            education_list.append(education_info)

            # 去重
            unique_education = []
            seen_schools = set()
            for edu in education_list:
                school_key = edu['school'][:20]  # 使用学校名前20个字符作为去重键
                if school_key not in seen_schools:
                    seen_schools.add(school_key)
                    unique_education.append(edu)

            return unique_education[:3]  # 最多返回3个教育背景

        except Exception as e:
            logger.error(f"教育背景提取失败: {e}")
            return []

    @classmethod
    def extract_work_experience(cls, text):
        """
        提取工作经历

        Args:
            text (str): 简历文本内容

        Returns:
            list: 工作经历列表
        """
        try:
            work_list = []

            # 工作经历匹配模式（包括实习经历）- 优化版
            patterns = [
                # 模式1: 标准时间 + 公司 + 职位格式
                r'(\d{4}[.\-/年]\d{1,2}[.\-/月]?[\s~\-至到]+(?:\d{4}[.\-/年]\d{1,2}[.\-/月]?|至今|现在))[\s\n\r]*([^\n\r]*(?:公司|集团|科技|技术|有限|股份|Corporation|Inc|Ltd|Co)[^\n\r]*?)[\s\n\r]*([^\n\r]*(?:工程师|开发|经理|主管|总监|架构师|实习生|助理|专员|Engineer|Developer|Manager|Intern)[^\n\r]*)',

                # 模式2: 公司名 + 职位名（简单格式）
                r'([^\n\r]*(?:公司|集团|科技|技术|有限|股份|Corporation|Inc|Ltd|Co)[^\n\r]*?)[\s\n\r]+([^\n\r]*(?:工程师|开发|经理|主管|总监|架构师|实习生|助理|专员|Engineer|Developer|Manager|Intern)[^\n\r]*)',

                # 模式3: 在XX公司实习/工作格式
                r'在([^\n\r]*(?:公司|集团|科技|技术|有限|股份|Corporation|Inc|Ltd|Co)[^\n\r]*?)(?:实习|工作|就职|任职)[\s，,]*(?:担任|任|做)?([^\n\r]*(?:工程师|开发|经理|主管|总监|架构师|实习生|助理|专员|Engineer|Developer|Manager|Intern)[^\n\r]*)',

                # 模式4: 项目名称 + 时间格式（如：产品工程实习生项目 20xx.xx—20xx.xx）
                r'([^\n\r]*(?:实习生|工程师|开发|项目)[^\n\r]*?)[\s\n\r]*(\d{4}[.\-/年]?\d{0,2}[.\-/月]?[\s~\-—至到]+\d{4}[.\-/年]?\d{0,2}[.\-/月]?)',

                # 模式5: 实习经历: 公司 职位格式
                r'(?:实习经历|工作经历|实习经验|工作经验)[\s：:]*([^\n\r]*(?:公司|集团|科技|技术|有限|股份|Corporation|Inc|Ltd|Co)[^\n\r]*?)[\s\n\r]*([^\n\r]*(?:工程师|开发|经理|主管|总监|架构师|实习生|助理|专员|Engineer|Developer|Manager|Intern)[^\n\r]*)',

                # 模式6: 时间 + 描述格式（如：2022年6月 - 2022年9月 参与Web应用开发）
                r'(\d{4}[.\-/年]\d{1,2}[.\-/月]?[\s~\-至到]+(?:\d{4}[.\-/年]\d{1,2}[.\-/月]?|至今|现在))[\s\n\r]*([^\n\r]*(?:参与|负责|协助|完成|开发|设计)[^\n\r]{10,100})',

                # 模式7: 某XX公司 + 职位（更宽泛的公司匹配）
                r'([^\n\r]*(?:某|XX)?[^\n\r]*(?:公司|集团|科技|技术|有限|股份|企业|机构|Corporation|Inc|Ltd|Co)[^\n\r]*?)[\s\n\r]*([^\n\r]*(?:工程师|开发|经理|主管|总监|架构师|实习生|助理|专员|Engineer|Developer|Manager|Intern)[^\n\r]*)',
            ]

            for i, pattern in enumerate(patterns):
                matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        work_info = {}

                        # 根据不同的模式处理匹配结果
                        if i == 0:  # 模式1: 标准时间 + 公司 + 职位格式
                            work_info = {
                                'period': groups[0].strip(),
                                'company': groups[1].strip(),
                                'position': groups[2].strip() if len(groups) > 2 else '员工',
                                'description': ''
                            }

                        elif i == 1:  # 模式2: 公司名 + 职位名（简单格式）
                            work_info = {
                                'period': '',
                                'company': groups[0].strip(),
                                'position': groups[1].strip(),
                                'description': ''
                            }

                        elif i == 2:  # 模式3: 在XX公司实习/工作格式
                            work_info = {
                                'period': '',
                                'company': groups[0].strip(),
                                'position': groups[1].strip() if len(groups) > 1 else '实习生',
                                'description': ''
                            }

                        elif i == 3:  # 模式4: 项目名称 + 时间格式
                            # 从项目名称中提取职位信息
                            project_name = groups[0].strip()
                            position = '实习生' if '实习生' in project_name else '工程师'
                            # 尝试从项目名称中提取公司信息
                            company = '项目相关公司'
                            if '工程' in project_name:
                                company = '工程公司'

                            work_info = {
                                'period': groups[1].strip(),
                                'company': company,
                                'position': position,
                                'description': project_name
                            }

                        elif i == 4:  # 模式5: 实习经历: 公司 职位格式
                            work_info = {
                                'period': '',
                                'company': groups[0].strip(),
                                'position': groups[1].strip(),
                                'description': ''
                            }

                        elif i == 5:  # 模式6: 时间 + 描述格式
                            # 从描述中尝试提取公司和职位信息
                            description = groups[1].strip()
                            company = '相关公司'
                            position = '实习生'

                            # 尝试从描述中提取更多信息
                            if '开发' in description:
                                position = '开发实习生'
                            elif '设计' in description:
                                position = '设计实习生'
                            elif '测试' in description:
                                position = '测试实习生'

                            work_info = {
                                'period': groups[0].strip(),
                                'company': company,
                                'position': position,
                                'description': description
                            }

                        elif i == 6:  # 模式7: 某XX公司 + 职位
                            work_info = {
                                'period': '',
                                'company': groups[0].strip(),
                                'position': groups[1].strip(),
                                'description': ''
                            }

                        # 清理和验证数据
                        if work_info.get('company') and len(work_info['company']) > 1:
                            # 清理公司名称
                            company = work_info['company']
                            # 移除常见的无用前缀
                            company = re.sub(r'^(实习经历|工作经历|实习经验|工作经验)[\s：:]*', '', company)
                            company = re.sub(r'^(某|XX)', '', company)  # 移除"某"、"XX"前缀
                            work_info['company'] = company.strip()

                            # 清理职位名称
                            position = work_info.get('position', '')
                            position = re.sub(r'^(某|XX)', '', position)
                            work_info['position'] = position.strip()

                            # 确保有基本信息
                            if work_info['company'] and work_info['position']:
                                work_list.append(work_info)

            # 去重
            unique_work = []
            seen_companies = set()
            for work in work_list:
                company_key = work['company'][:20]
                if company_key not in seen_companies:
                    seen_companies.add(company_key)
                    unique_work.append(work)

            return unique_work[:5]  # 最多返回5个工作经历

        except Exception as e:
            logger.error(f"工作经历提取失败: {e}")
            return []

    @classmethod
    def recommend_positions(cls, skills):
        """
        基于技能推荐岗位

        Args:
            skills (list): 技能列表

        Returns:
            list: 推荐岗位列表
        """
        try:
            skill_set = set(skill.lower() for skill in skills)
            position_scores = {}

            for position, keywords in cls.POSITION_KEYWORDS.items():
                score = 0
                matched_keywords = []

                for keyword in keywords:
                    if keyword.lower() in skill_set:
                        score += 1
                        matched_keywords.append(keyword)

                if score > 0:
                    position_scores[position] = {
                        'score': score,
                        'match_rate': score / len(keywords),
                        'matched_skills': matched_keywords
                    }

            # 按匹配度排序
            sorted_positions = sorted(
                position_scores.items(),
                key=lambda x: (x[1]['score'], x[1]['match_rate']),
                reverse=True
            )

            # 返回前5个推荐岗位
            recommendations = []
            for position, data in sorted_positions[:5]:
                recommendations.append({
                    'position': position,
                    'match_score': data['score'],
                    'match_rate': round(data['match_rate'] * 100, 1),
                    'matched_skills': data['matched_skills']
                })

            return recommendations

        except Exception as e:
            logger.error(f"岗位推荐失败: {e}")
            return []

    @classmethod
    def analyze_resume(cls, text):
        """
        综合分析简历内容（升级版）

        Args:
            text (str): 简历文本内容

        Returns:
            dict: 分析结果
        """
        try:
            logger.info("开始升级版简历分析...")

            # 基础提取
            skills = cls.extract_skills(text)
            projects = cls.extract_projects(text)
            personal_info = cls.extract_personal_info(text)
            education = cls.extract_education(text)
            work_experience = cls.extract_work_experience(text)

            # 岗位推荐
            recommended_positions = cls.recommend_positions(skills)

            # 经验年限估算
            experience_years = 0
            if work_experience:
                for work in work_experience:
                    period = work.get('period', '')
                    years = re.findall(r'(\d{4})', period)
                    if len(years) >= 2:
                        try:
                            start_year = int(years[0])
                            end_year = int(years[-1])
                            experience_years += max(0, end_year - start_year)
                        except:
                            pass

            # 技能分类统计
            skill_categories = {}
            for category, category_skills in cls.SKILL_KEYWORDS.items():
                matched = [skill for skill in skills if skill in category_skills]
                if matched:
                    skill_categories[category] = matched

            # 统计信息
            stats = {
                'total_skills': len(skills),
                'total_projects': len(projects),
                'total_education': len(education),
                'total_work_experience': len(work_experience),
                'estimated_experience_years': experience_years,
                'text_length': len(text),
                'has_contact_info': bool(personal_info.get('phone') or personal_info.get('email')),
                'has_education': len(education) > 0,
                'skill_categories': list(skill_categories.keys())
            }

            # 简历完整度评分
            completeness_score = 0
            if personal_info.get('name'): completeness_score += 10
            if personal_info.get('phone'): completeness_score += 15
            if personal_info.get('email'): completeness_score += 15
            if education: completeness_score += 20
            if work_experience: completeness_score += 20
            if skills: completeness_score += 15
            if projects: completeness_score += 5

            result = {
                'personal_info': personal_info,
                'skills': skills,
                'skill_categories': skill_categories,
                'projects': projects,
                'education': education,
                'work_experience': work_experience,
                'recommended_positions': recommended_positions,
                'stats': stats,
                'completeness_score': completeness_score,
                'analysis_time': datetime.now().isoformat(),
                'analyzer_version': '2.0'
            }

            logger.info(f"升级版简历分析完成: 技能{len(skills)}个, 项目{len(projects)}个, 教育{len(education)}个, 工作{len(work_experience)}个, 完整度{completeness_score}%")
            return result

        except Exception as e:
            logger.error(f"升级版简历分析失败: {e}")
            return {
                'personal_info': {},
                'skills': [],
                'skill_categories': {},
                'projects': [],
                'education': [],
                'work_experience': [],
                'recommended_positions': [],
                'stats': {},
                'completeness_score': 0,
                'error': str(e),
                'analyzer_version': '2.0'
            }