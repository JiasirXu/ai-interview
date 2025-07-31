<template>
  <div class="report-page">
    <div class="breadcrumb">
      <span class="breadcrumb-item">测评报告</span>
      <span class="breadcrumb-divider">></span>
      <span class="breadcrumb-item active">结果分析</span>
    </div>
    
    <div class="score-container">
      <div class="score-card">
        <div class="score-main">
          <h1 class="total-score">85/100</h1>
          <div class="trophy-container">
            <SvgIcon name="trophy" class="trophy-icon" />
            <span class="grade">评级：A（优秀）</span>
              </div>
            </div>
        <div class="metrics-container">
          <div class="metric-item">
            <div class="metric-label">击败全国候选人</div>
            <div class="metric-value">89%</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">岗位匹配度</div>
            <div class="metric-value">92%</div>
          </div>
              </div>
            </div>
          </div>
          
    <div class="ability-scores">
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon">
            <SvgIcon name="technical-ability" />
          </div>
          <span>技术能力</span>
        </div>
        <div class="ability-score">88</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '88%' }"></div>
        </div>
      </div>
      
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon">
            <SvgIcon name="expression-logic" />
          </div>
          <span>表达逻辑</span>
        </div>
        <div class="ability-score">82</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '82%' }"></div>
        </div>
      </div>
      
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon">
            <SvgIcon name="adaptability" />
          </div>
          <span>应变能力</span>
        </div>
        <div class="ability-score">76</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '76%' }"></div>
        </div>
      </div>
      
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon">
            <SvgIcon name="behavior-etiquette" />
          </div>
          <span>行为礼仪</span>
        </div>
        <div class="ability-score">91</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '91%' }"></div>
        </div>
      </div>
      
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon collaboration-icon">
            <SvgIcon name="collaboration" />
          </div>
          <span>协作意识</span>
        </div>
        <div class="ability-score">68</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '68%' }"></div>
        </div>
      </div>
      
      <div class="ability-card">
        <div class="ability-header">
          <div class="ability-icon">
            <SvgIcon name="cultural-fit" />
          </div>
          <span>文化匹配</span>
        </div>
        <div class="ability-score">80</div>
        <div class="score-bar">
          <div class="bar-fill" :style="{ width: '80%' }"></div>
        </div>
      </div>
    </div>
    
    <!-- 高光时刻和低分片段 -->
    <div class="highlight-lowlight">
      <div class="highlight-section">
        <div class="section-tag good">
          <SvgIcon name="advantages" />
          <span>高光时刻</span>
        </div>
        <ul class="timestamp-list">
          <li><span class="timestamp">04:32</span> 巧妙转化"最大缺点"为成长案例</li>
          <li><span class="timestamp">12:15</span> 手写LRU缓存代码（最优时间复杂度）</li>
        </ul>
      </div>
      
      <div class="highlight-section">
        <div class="section-tag warning">
          <SvgIcon name="disadvantages" />
          <span>低分片段</span>
        </div>
        <ul class="timestamp-list">
          <li><span class="timestamp">07:40</span> 混淆TCP/UDP应用场景</li>
          <li><span class="timestamp">09:20</span> 压力面时陈述速度减慢30%</li>
        </ul>
      </div>
    </div>

    <div class="detail-sections">
      <div class="detail-section">
        <div class="section-header">
          <h3>技术能力</h3>
          <div class="section-score">(88/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>算法实现完整，代码结构清晰（击败95%用户）</li>
            <li>系统设计考虑高可用性（如Redis缓存+DB一致性方案）</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>分布式事务（如Seata）解释不够深入</li>
            <li>未提及监控（Prometheus/Grafana）</li>
          </ul>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-header">
          <h3>表达逻辑</h3>
          <div class="section-score">(82/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>STAR模型使用熟练（情境-任务-行动-结果完整90%）</li>
            <li>技术术语准确（如准确区分HTTP/2 vs WebSocket）</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>回答前5秒停顿"呃"、"嗯"残词过多（共7次）</li>
            <li>部分解释过于技术化（非技术面试官可能困惑）</li>
          </ul>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-header">
          <h3>应变能力</h3>
          <div class="section-score">(76/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>面对突发问题能快速调整思路（反应时间平均3秒）</li>
            <li>压力下保持冷静，逻辑清晰（压力测试通过率85%）</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>遇到复杂场景时容易过度思考，影响决策速度</li>
            <li>对不熟悉领域的问题缺乏灵活的解决方案</li>
          </ul>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-header">
          <h3>行为礼仪</h3>
          <div class="section-score">(91/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>坐姿端正，眼神交流自然（专业度评分95%）</li>
            <li>语速适中，声音清晰，表达自信（沟通效果优秀）</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>偶尔出现小幅度手势过多的情况</li>
            <li>在紧张时刻会有轻微的语调变化</li>
          </ul>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-header">
          <h3>协作意识</h3>
          <div class="section-score">(68/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>在团队项目中主动承担责任，乐于分享知识</li>
            <li>能够有效协调不同角色，促进团队协作</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>在跨部门协作中偶尔缺乏主动沟通意识</li>
            <li>团队冲突处理能力有待提升，需要更多实践</li>
          </ul>
        </div>
      </div>
      
      <div class="detail-section">
        <div class="section-header">
          <h3>文化匹配</h3>
          <div class="section-score">(80/100)</div>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag good">
            <SvgIcon name="advantages" />
            <span>优势</span>
          </div>
          <ul class="assessment-list">
            <li>价值观与企业文化高度契合（匹配度90%）</li>
            <li>团队协作意识强，具备良好的沟通合作能力</li>
          </ul>
        </div>
        
        <div class="assessment-group">
          <div class="assessment-tag warning">
            <SvgIcon name="disadvantages" />
            <span>劣势</span>
          </div>
          <ul class="assessment-list">
            <li>对企业具体业务流程了解不够深入</li>
            <li>需要时间适应企业的工作节奏和管理风格</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import SvgIcon from '@/components/common/SvgIcon.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 在真实应用中，这些数据将通过API获取
const interviewResults = ref(null)

// 根据面试ID获取测评数据
const fetchInterviewResults = async (interviewId) => {
  try {
    // 在实际应用中，这里会调用API获取数据
    // const response = await api.getInterviewResults(interviewId)
    // interviewResults.value = response.data
    
    // 模拟数据
    interviewResults.value = {
    score: 85,
      grade: 'A',
      percentile: 89,
      jobMatch: 92,
      abilities: {
    technical: 88,
        expression: 82,
        adaptability: 76,
        behavior: 91,
        english: 68,
        culture: 80
      },
      technicalAssessment: {
        score: 88,
        strengths: [
          '算法实现完整，代码结构清晰（击败95%用户）',
          '系统设计考虑高可用性（如Redis缓存+DB一致性方案）'
        ],
        weaknesses: [
          '分布式事务（如Seata）解释不够深入',
          '未提及监控（Prometheus/Grafana）'
        ]
      },
      expressionAssessment: {
        score: 82,
        strengths: [
          'STAR模型使用熟练（情境-任务-行动-结果完整90%）',
          '技术术语准确（如准确区分HTTP/2 vs WebSocket）'
        ],
        weaknesses: [
          '回答前5秒停顿"呃"、"嗯"残词过多（共7次）',
          '部分解释过于技术化（非技术面试官可能困惑）'
        ]
      },
      highlights: [
        { time: '04:32', description: '巧妙转化"最大缺点"为成长案例' },
        { time: '12:15', description: '手写LRU缓存代码（最优时间复杂度）' }
      ],
      lowlights: [
        { time: '07:40', description: '混淆TCP/UDP应用场景' },
        { time: '09:20', description: '压力面时陈述速度减慢30%' }
      ]
    }
  } catch (error) {
    console.error('获取面试结果失败:', error)
  }
}

onMounted(() => {
  // 获取URL中的面试ID参数
  // const interviewId = route.params.id || '1'
  // fetchInterviewResults(interviewId)
  
  // 暂时使用模拟数据
  fetchInterviewResults('1')
})
</script>

<style lang="scss" scoped>
.report-page {
  padding: 24px 32px;
  background-color: #fff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #86868b;
}

.breadcrumb-item {
  color: #86868b;
}

.breadcrumb-item.active {
  color: #722ED1;
}

.breadcrumb-divider {
  margin: 0 8px;
  color: #86868b;
}

.score-container {
  margin-bottom: 32px;
}

.score-card {
  background: linear-gradient(90deg, #f6eeff 0%, #ffffff 100%); /* 从紫色渐变到白色 */
  border-radius: 8px;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.total-score {
  font-size: 42px;
  font-weight: 700;
  margin: 0;
  color: #111827;
  line-height: 1;
}

.trophy-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trophy-icon {
  width: 24px;
  height: 24px;
  color: #F59E0B; /* 金色 */
}

.grade {
  font-size: 16px;
  font-weight: 500;
  color: #111827;
}

.metrics-container {
  display: flex;
  flex-direction: row; /* 改为并排显示 */
  gap: 48px; /* 调整间距 */
}

.metric-item {
  text-align: left; /* 左对齐 */
}

.metric-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

.ability-scores {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.ability-card {
  background-color: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ability-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #111827;
}

.ability-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .svg-icon {
    width: 20px;
    height: 20px;
    color: #722ED1;
  }
}

/* 协作意识图标特殊颜色 */
.collaboration-icon .svg-icon {
  color: #722ED1 !important; /* 紫色，与其他能力卡片保持一致 */
}

.ability-score {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #111827;
}

.score-bar {
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #722ED1 0%, #a855f7 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.detail-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #111827;
}

.section-score {
  color: #6b7280;
  font-size: 16px;
}

.assessment-group {
  margin-bottom: 16px;
}

.assessment-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  
  .svg-icon {
    width: 16px;
    height: 16px;
  }
}

.assessment-tag.good {
  color: #16a34a;
  
  .svg-icon {
    color: #16a34a;
  }
}

.assessment-tag.warning {
  color: #f59e0b;
  
  .svg-icon {
    color: #f59e0b;
  }
}

.assessment-list {
  list-style-type: none;
  padding-left: 28px;
  margin: 0;
}

.assessment-list li {
  position: relative;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

.assessment-list li::before {
  content: "•";
  position: absolute;
  left: -16px;
}

.highlight-lowlight {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.highlight-section {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 16px;

  .svg-icon {
    width: 20px;
    height: 20px;
  }
}

.section-tag.good {
  color: #16a34a;
  
  .svg-icon {
    color: #16a34a;
  }
}

.section-tag.warning {
  color: #f59e0b;
  
  .svg-icon {
    color: #f59e0b;
  }
}

.timestamp-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.timestamp-list li {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.timestamp {
  font-weight: 500;
  color: #6b7280;
}

// 图标样式
.icon-code::before {
  content: "</>";
  color: #722ED1;
}

.icon-chat::before {
  content: "💬";
}

.icon-solution::before {
  content: "🧩";
}

.icon-behavior::before {
  content: "👤";
}

.icon-language::before {
  content: "🌐";
}

.icon-culture::before {
  content: "🏢";
}

.icon-check::before {
  content: "✓";
}

.icon-warning::before {
  content: "⚠";
}

// 响应式设计
@media (max-width: 768px) {
  .report-page {
    padding: 16px;
  }
  
  .score-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .metrics-container {
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
  }
  
  .metric-item {
    text-align: left;
  }
  
  .ability-scores {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .highlight-lowlight {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .ability-scores {
    grid-template-columns: 1fr;
  }

  .metrics-container {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>