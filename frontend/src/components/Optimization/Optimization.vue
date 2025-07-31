<template>
  <div class="topic-analysis-page">
    <div class="header-actions">
      <div class="breadcrumb">
        <span class="breadcrumb-item">优化建议</span>
        <span class="breadcrumb-divider">></span>
        <span class="breadcrumb-item active">题目解析</span>
      </div>
    </div>
    

    
    <div class="svg-container">
      <img src="./FRAME-extra.svg" alt="题目分析框架" class="topic-frame" />
    </div>

    <div class="page-container">
      <div class="topics-container" ref="topicsContainer">
        <el-skeleton :loading="loading" animated :throttle="500">
          <template #template>
            <div class="skeleton-content">
              <el-skeleton-item variant="h3" style="width: 80%" />
              <el-skeleton-item variant="text" style="margin-top: 16px; height: 100px" />
              <el-skeleton-item variant="text" style="margin-top: 16px; height: 200px" />
            </div>
          </template>
          <template #default>
            <div v-for="(topic, index) in topics" :key="index" class="topic-card" :class="{ collapsed: topic.collapsed }" :id="`topic-${index + 1}`">
              <div class="topic-header" @click="toggleTopic(index)">
                <div class="topic-index">{{ index + 1 }}</div>
                <div class="topic-title">{{ topic.title }}</div>
                <div class="collapse-toggle">
                  <i :class="topic.collapsed ? 'el-icon-arrow-right' : 'el-icon-arrow-down'"></i>
                </div>
              </div>
        
              <div v-show="!topic.collapsed" class="topic-content">
                <div class="user-answer section">
                   <div class="section-header">
                     用户回答
                   </div>
                  <div class="section-content">{{ topic.userAnswer }}</div>
                  <div class="audio-playback" v-if="topic.audioUrl">
                    <div class="audio-control">
                      <el-button size="small" type="primary" circle>
                        <i class="el-icon-video-play"></i>
                      </el-button>
                      <span>播放回答录音</span>
                    </div>
                  </div>
                </div>
                
                <div class="reference-answer section">
                  <div class="section-header">
                    参考答案
                  </div>
                  <div class="section-content" v-html="topic.referenceAnswer"></div>
                </div>
                
                <div class="analysis section">
                  <div class="section-header">答案分析</div>
                  <div class="section-content">
                    <div class="analysis-strength">
                      <div class="analysis-label good">优点</div>
                      <ul class="analysis-list">
                        <li v-for="(strength, i) in topic.analysis.strengths" :key="i">
                          {{ strength }}
                        </li>
                      </ul>
                    </div>
                    
                    <div class="analysis-weakness">
                      <div class="analysis-label warning">不足</div>
                      <ul class="analysis-list">
                        <li v-for="(weakness, i) in topic.analysis.weaknesses" :key="i">
                          {{ weakness }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                <div class="improvement section">
                  <div class="section-header">提升建议</div>
                  <div class="section-content">
                    <ul class="improvement-list">
                      <li v-for="(suggestion, i) in topic.suggestions" :key="i">
                        {{ suggestion }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
        
              </div><!-- 闭合topic-card -->
          </template>
        </el-skeleton>
      </div>
    </div>
    
    <div class="page-footer">
      <div class="next-steps">
        <p>完成题目解析后，建议您：</p>
        <div class="steps-buttons">
          <el-button type="primary" plain @click="exportReport" :loading="exporting">导出分析报告</el-button>
          <el-button type="success" plain @click="navigateToInterview">再次模拟面试</el-button>
          <el-button type="info" plain @click="navigateToProfile">返回个人中心</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

// 模拟数据 - 实际应用中应从API获取
const topics = ref([
  {
    id: 1,
    title: '请解释什么是虚拟DOM，以及它的优势',
    collapsed: false,
    userAnswer: '虚拟DOM就是...嗯...一个轻量级的DOM副本，可以提升性能。',
    referenceAnswer: '虚拟DOM是JavaScript对象表示的DOM结构的轻量级副本。通过过程性的diff算法计算出最小要更新后批量更新真实DOM。它的核心优势在于通过内存中的计算减少了对真实DOM的频繁操作，提高了性能表现。<br><br>在React等框架中，虚拟DOM机制能处理组件更新时的性能瓶颈，同时实现了跨平台能力。为开发者提供了声明式的编程体验，自动化了复杂的DOM操作过程，保证了运行的性能。',
    analysis: {
      strengths: [
        '基本理解了虚拟DOM的概念',
        '提到了提升性能的优势点'
      ],
      weaknesses: [
        '回答过于简短，缺乏详细解释',
        '未提及虚拟DOM如何工作',
        '没有提及跨平台和声明式编程的优势'
      ]
    },
    suggestions: [
      '系统学习虚拟DOM的工作原理和实现机制',
      '通过具体框架(React/Vue)理解虚拟DOM的实际应用',
      '学习diff算法的基本原理'
    ]
  },
  {
    id: 2,
    title: '如果让你设计一个短链接服务，你会考虑哪些方面？',
    collapsed: false,
    userAnswer: '用哈希算法生成短码，存在数据库，然后做转发。',
    referenceAnswer: '设计一个全面的短链接服务需要综合考虑创建方法、存储方案、高并发处理和监控维护等诸多环节：<br><br>1. <b>短码生成</b>：可采用自增ID+62进制编码法生成6-8位短码；也可采用哈希算法(如MD5)截取部分作为短码，需处理哈希冲突<br>2. <b>存储方案</b>：高性能需求下应采用Redis等缓存+数据库的混合存储方案，确保读取性能<br>3. <b>高可用设计</b>：服务需要水平扩展能力，并设计一致性哈希等策略避免单点故障<br>4. <b>安全监控</b>：建立点击量统计、反爬虫机制以及访问权限控制<br>5. <b>过期策略</b>：制定合理的短链过期策略和定期清理机制',
    analysis: {
      strengths: [
        '提到了哈希算法生成短码的基本思路',
        '理解了短链接服务的基本功能需求'
      ],
      weaknesses: [
        '回答过于简略，缺乏系统设计思维',
        '未考虑高并发场景下的性能问题',
        '没有提及安全性和监控需求',
        '未考虑短链接过期和统计分析功能'
      ]
    },
    suggestions: [
      '学习系统设计的基本方法论，尤其是高并发系统设计',
      '了解缓存与数据库配合使用的最佳实践',
      '关注安全性和可维护性在设计中的重要性'
    ]
  },
  {
    id: 3,
    title: 'React的useEffect和useLayoutEffect有什么区别？',
    collapsed: false,
    userAnswer: '都是副作用钩子...好像一个是在渲染前，一个是在渲染后？',
    referenceAnswer: 'useEffect和useLayoutEffect虽然都是用于处理副作用的钩子函数，但在执行时机和使用场景上有明显差异。<br><br>useEffect会在DOM更新完成后异步执行，不会阻塞浏览器渲染，适用于大多数不直接操作DOM或不要求同步执行的副作用，如数据获取、订阅设置等场景；而useLayoutEffect则会在DOM变更后、浏览器绘制前同步执行，会阻塞浏览器渲染，适用于需要直接操作DOM并且要立即计算布局的场景，如需要防止页面闪烁的情况。<br><br>在性能方面，useEffect是首选，因为它不会阻塞渲染过程；只有当确实需要同步操作DOM并立即生效时，才应该使用useLayoutEffect。',
    analysis: {
      strengths: [
        '知道两者都是处理副作用的钩子函数',
        '对执行时机有基本的了解'
      ],
      weaknesses: [
        '回答不够确定，表达模糊',
        '未能清晰区分两者的使用场景',
        '没有提及对性能的影响',
        '未解释何时应该选择使用哪个钩子'
      ]
    },
    suggestions: [
      '深入学习React Hooks的执行机制和渲染流程',
      '通过实际案例理解两种钩子的差异和最佳使用场景',
      '掌握React中的性能优化原则'
    ]
  },
  {
    id: 4,
    title: '请解释JavaScript中的闭包概念及其应用场景',
    collapsed: false,
    userAnswer: '闭包就是函数里面的函数，可以访问外部变量。',
    referenceAnswer: '闭包是JavaScript中的一个重要概念，指的是函数能够访问其词法作用域外的变量，即使在其外部函数已经返回之后。<br><br>闭包的核心特性：<br>1. 内部函数可以访问外部函数的变量<br>2. 外部函数返回后，其变量仍然被内部函数引用而不会被垃圾回收<br>3. 每次调用外部函数都会创建新的闭包<br><br>常见应用场景：<br>- 数据私有化和封装<br>- 模块化开发<br>- 回调函数和事件处理<br>- 函数柯里化<br>- 防抖和节流函数',
    analysis: {
      strengths: [
        '理解了闭包的基本概念',
        '知道内部函数可以访问外部变量'
      ],
      weaknesses: [
        '对闭包的定义过于简化',
        '未提及闭包的核心机制',
        '没有说明闭包的实际应用场景',
        '缺乏对内存管理的理解'
      ]
    },
    suggestions: [
      '深入学习JavaScript的作用域链和执行上下文',
      '通过实际代码示例理解闭包的工作原理',
      '学习闭包在实际开发中的应用模式'
    ]
  },
  {
    id: 5,
    title: '什么是RESTful API？请说明其设计原则',
    collapsed: false,
    userAnswer: 'RESTful API就是用HTTP方法来操作资源的接口。',
    referenceAnswer: 'RESTful API是基于REST（Representational State Transfer）架构风格设计的Web API，它使用HTTP协议的标准方法来操作资源。<br><br>核心设计原则：<br>1. <b>资源导向</b>：每个URL代表一个资源<br>2. <b>统一接口</b>：使用标准HTTP方法（GET、POST、PUT、DELETE等）<br>3. <b>无状态</b>：每个请求都包含处理该请求所需的所有信息<br>4. <b>可缓存</b>：响应应该明确标识是否可缓存<br>5. <b>分层系统</b>：客户端无需知道是否直接连接到最终服务器<br>6. <b>统一资源标识</b>：使用URI唯一标识资源<br><br>最佳实践包括使用合适的HTTP状态码、版本控制、错误处理等。',
    analysis: {
      strengths: [
        '理解了RESTful API的基本概念',
        '知道使用HTTP方法操作资源'
      ],
      weaknesses: [
        '对REST原则理解不够深入',
        '未提及无状态、可缓存等重要特性',
        '缺乏对资源设计的理解',
        '没有涉及最佳实践'
      ]
    },
    suggestions: [
      '系统学习REST架构的六大约束原则',
      '实践设计符合RESTful规范的API',
      '了解API版本控制和错误处理最佳实践'
    ]
  },
  {
    id: 6,
    title: '请解释数据库事务的ACID特性',
    collapsed: false,
    userAnswer: 'ACID是原子性、一致性、隔离性、持久性，保证数据库操作的可靠性。',
    referenceAnswer: 'ACID是数据库事务必须具备的四个基本特性，确保数据库操作的可靠性和一致性：<br><br><b>Atomicity（原子性）</b>：事务是一个不可分割的工作单位，要么全部执行成功，要么全部回滚，不存在部分执行的情况。<br><br><b>Consistency（一致性）</b>：事务执行前后，数据库必须处于一致性状态，所有的完整性约束都必须得到满足。<br><br><b>Isolation（隔离性）</b>：并发执行的事务之间不能相互干扰，每个事务都感觉不到其他事务的存在。隔离级别包括读未提交、读已提交、可重复读、串行化。<br><br><b>Durability（持久性）</b>：事务一旦提交，其对数据库的修改就是永久性的，即使系统故障也不会丢失。',
    analysis: {
      strengths: [
        '正确说出了ACID四个特性的名称',
        '理解了ACID的基本作用'
      ],
      weaknesses: [
        '对每个特性的具体含义解释不够详细',
        '未提及隔离级别的概念',
        '缺乏实际应用场景的理解',
        '没有说明ACID特性之间的关系'
      ]
    },
    suggestions: [
      '深入学习每个ACID特性的具体实现机制',
      '了解不同数据库系统对ACID的支持程度',
      '学习事务隔离级别和并发控制'
    ]
  },
  {
    id: 7,
    title: '什么是微服务架构？它有哪些优缺点？',
    collapsed: false,
    userAnswer: '微服务就是把大的应用拆分成小的服务，每个服务独立部署。',
    referenceAnswer: '微服务架构是一种将单一应用程序开发为一组小型服务的方法，每个服务运行在自己的进程中，并使用轻量级机制（通常是HTTP API）进行通信。<br><br><b>主要优点：</b><br>- 技术栈灵活性：每个服务可以使用不同的技术栈<br>- 独立部署和扩展：服务可以独立部署、更新和扩展<br>- 故障隔离：单个服务的故障不会影响整个系统<br>- 团队自治：小团队可以独立开发和维护服务<br>- 更好的可测试性和可维护性<br><br><b>主要缺点：</b><br>- 分布式系统复杂性：网络延迟、数据一致性等问题<br>- 运维复杂度增加：需要管理更多的服务实例<br>- 服务间通信开销<br>- 数据管理复杂性<br>- 调试和监控困难',
    analysis: {
      strengths: [
        '理解了微服务的基本概念',
        '知道服务拆分和独立部署的特点'
      ],
      weaknesses: [
        '对微服务架构的理解过于简化',
        '未提及微服务的具体优缺点',
        '缺乏对分布式系统复杂性的认识',
        '没有涉及微服务的实施挑战'
      ]
    },
    suggestions: [
      '深入学习分布式系统的基本概念和挑战',
      '了解微服务架构的设计模式和最佳实践',
      '学习服务发现、配置管理、监控等微服务基础设施'
    ]
  },
  {
    id: 8,
    title: '请解释HTTP和HTTPS的区别',
    collapsed: false,
    userAnswer: 'HTTPS比HTTP多了一个S，就是安全的意思，用了SSL加密。',
    referenceAnswer: 'HTTP和HTTPS是两种不同的网络通信协议，主要区别在于安全性和数据传输方式：<br><br><b>HTTP（超文本传输协议）：</b><br>- 明文传输，数据未加密<br>- 默认端口80<br>- 无法验证服务器身份<br>- 数据容易被窃听、篡改<br>- 连接建立简单，性能较好<br><br><b>HTTPS（安全超文本传输协议）：</b><br>- 基于SSL/TLS加密传输<br>- 默认端口443<br>- 通过数字证书验证服务器身份<br>- 提供数据完整性和机密性保护<br>- 连接建立需要额外的握手过程<br><br>HTTPS通过SSL/TLS协议提供三重保护：加密（防窃听）、完整性（防篡改）、身份验证（防冒充）。',
    analysis: {
      strengths: [
        '知道HTTPS比HTTP更安全',
        '了解SSL加密的概念'
      ],
      weaknesses: [
        '对两者区别的理解过于简化',
        '未提及端口、证书等技术细节',
        '缺乏对SSL/TLS工作原理的理解',
        '没有说明HTTPS的具体安全机制'
      ]
    },
    suggestions: [
      '深入学习SSL/TLS协议的工作原理',
      '了解数字证书和PKI基础设施',
      '学习HTTPS的性能优化和最佳实践'
    ]
  },
  {
    id: 9,
    title: '什么是Docker？它解决了什么问题？',
    collapsed: false,
    userAnswer: 'Docker是容器技术，可以把应用打包，在不同环境运行。',
    referenceAnswer: 'Docker是一个开源的容器化平台，它使用Linux容器技术来创建、部署和管理应用程序。<br><br><b>核心概念：</b><br>- 镜像（Image）：应用程序的只读模板<br>- 容器（Container）：镜像的运行实例<br>- Dockerfile：构建镜像的脚本文件<br>- 仓库（Registry）：存储和分发镜像的服务<br><br><b>解决的主要问题：</b><br>- <b>环境一致性</b>："在我机器上能运行"的问题<br>- <b>资源利用率</b>：比虚拟机更轻量级<br>- <b>快速部署</b>：秒级启动，快速扩缩容<br>- <b>依赖管理</b>：应用和依赖打包在一起<br>- <b>微服务支持</b>：便于微服务架构的实施<br>- <b>CI/CD集成</b>：简化持续集成和部署流程',
    analysis: {
      strengths: [
        '理解了Docker的基本概念',
        '知道容器化和跨环境运行的特点'
      ],
      weaknesses: [
        '对Docker核心概念理解不够深入',
        '未具体说明Docker解决的问题',
        '缺乏对容器和虚拟机区别的理解',
        '没有涉及Docker的实际应用场景'
      ]
    },
    suggestions: [
      '深入学习容器技术的原理和实现',
      '实践Docker的基本操作和Dockerfile编写',
      '了解容器编排工具如Kubernetes'
    ]
  },
  {
    id: 10,
    title: '请解释什么是负载均衡，常见的负载均衡算法有哪些？',
    collapsed: false,
    userAnswer: '负载均衡就是把请求分发到多个服务器，有轮询、随机等算法。',
    referenceAnswer: '负载均衡是一种在多个服务器之间分配网络流量的技术，目的是提高系统的可用性、可靠性和性能。<br><br><b>主要作用：</b><br>- 提高系统吞吐量和响应速度<br>- 避免单点故障<br>- 实现水平扩展<br>- 优化资源利用率<br><br><b>常见负载均衡算法：</b><br>1. <b>轮询（Round Robin）</b>：按顺序依次分配请求<br>2. <b>加权轮询</b>：根据服务器权重分配请求<br>3. <b>随机（Random）</b>：随机选择服务器<br>4. <b>最少连接</b>：选择当前连接数最少的服务器<br>5. <b>IP哈希</b>：根据客户端IP哈希值选择服务器<br>6. <b>最短响应时间</b>：选择响应时间最短的服务器<br><br>负载均衡可以在不同层次实现：硬件负载均衡器、软件负载均衡器、DNS负载均衡等。',
    analysis: {
      strengths: [
        '理解了负载均衡的基本概念',
        '知道轮询和随机等基本算法'
      ],
      weaknesses: [
        '对负载均衡的作用理解不够全面',
        '算法介绍过于简单，缺乏细节',
        '未提及不同类型的负载均衡器',
        '缺乏对实际应用场景的理解'
      ]
    },
    suggestions: [
      '深入学习各种负载均衡算法的适用场景',
      '了解不同层次负载均衡的实现方式',
      '学习负载均衡在高可用架构中的应用'
    ]
  }
]);

const router = useRouter();

// 移除当前选中题目相关逻辑，改为垂直展示所有题目

// 模拟加载状态
const loading = ref(false);
const exporting = ref(false);

const topicsContainer = ref(null);

// 挂载时从API获取题目数据
onMounted(() => {
  // 实际应用中这里会调用API获取题目和解析数据
  const fetchTopics = async () => {
    loading.value = true;
    try {
      // 模拟API请求延迟
      await new Promise(resolve => setTimeout(resolve, 800));
      // const response = await api.getTopics();
      // topics.value = response.data;
      
      // 现有的模拟数据已经设置
    } catch (error) {
      console.error(error);
      ElMessage.error('获取题目数据失败');
    } finally {
      loading.value = false;
    }
  };
  
  fetchTopics();
});

// 导出分析报告
const exportReport = async () => {
  exporting.value = true;
  if (!topicsContainer.value) {
    ElMessage.error('无法找到报告内容');
    exporting.value = false;
    return;
  }

  try {
    const a4Width = 592.28;
    const a4Height = 841.89;
    let pdf = new jsPDF('p', 'pt', 'a4');
    
    // 获取所有题目卡片
    const topicCards = topicsContainer.value.querySelectorAll('.topic-card');
    
    for (let i = 0; i < topicCards.length; i++) {
      const topicCard = topicCards[i];
      
      // 为每个题目卡片生成canvas
      const canvas = await html2canvas(topicCard, {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff',
        width: topicCard.scrollWidth,
        height: topicCard.scrollHeight
      });
      
      const contentWidth = canvas.width;
      const contentHeight = canvas.height;
      
      // 计算缩放比例，确保内容适合A4页面
      const scaleX = a4Width / contentWidth;
      const scaleY = a4Height / contentHeight;
      const scale = Math.min(scaleX, scaleY, 1); // 不放大，只缩小
      
      const imgWidth = contentWidth * scale;
      const imgHeight = contentHeight * scale;
      
      // 居中显示
      const x = (a4Width - imgWidth) / 2;
      const y = (a4Height - imgHeight) / 2;
      
      const pageData = canvas.toDataURL('image/jpeg', 1.0);
      
      // 如果不是第一页，添加新页面
      if (i > 0) {
        pdf.addPage();
      }
      
      // 添加题目到PDF
      pdf.addImage(pageData, 'JPEG', x, y, imgWidth, imgHeight);
    }
    
    pdf.save('题目解析报告.pdf');
    ElMessage.success('报告导出成功');

  } catch (error) {
    console.error('导出PDF时出错:', error);
    ElMessage.error('导出报告失败，请稍后重试');
  } finally {
    exporting.value = false;
  }
};

const navigateToInterview = () => {
  router.push({ name: 'InterviewMain' });
};

const navigateToProfile = () => {
  router.push({ name: 'PersonalInfo' });
};

// 切换题目折叠状态
const toggleTopic = (index) => {
  topics.value[index].collapsed = !topics.value[index].collapsed;
};
</script>

<style lang="scss" scoped>
.topic-analysis-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  color: var(--el-text-color-primary);
  background-color: #fff;
  min-height: 100vh;
  
  // 添加平滑滚动效果
  scroll-behavior: smooth;
  
  // 为锚点添加滚动偏移，避免被固定导航遮挡
  scroll-padding-top: 70px;
}

.svg-container {
  display: none; /* 先隐藏，按需使用 */
}

.topic-frame {
  width: 100%;
  height: auto;
  max-width: 1136px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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



.page-container {
  min-height: calc(100vh - 150px);
}

.topics-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.topic-card {
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  padding: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &:hover {
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
    border-color: #d0d7de;
  }
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 3px;
    width: 100%;
    background-color: #722ED1;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }
  
  // 折叠状态样式
  &.collapsed {
    padding: 0;
    
    .topic-header {
      margin-bottom: 0;
      padding: 20px 24px;
      border-bottom: none;
    }
  }
}

.topic-number {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #7245d1;
  color: white;
  font-weight: 600;
  margin-right: 16px;
  font-size: 18px;
}

.topic-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: rgba(114, 69, 209, 0.05);
    margin: 0 -24px;
    padding-left: 24px;
    padding-right: 24px;
  }
}

.topic-index {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #7245d1;
  color: white;
  font-weight: 600;
  font-size: 18px;
  margin-right: 16px;
}

.topic-title {
  font-size: 18px;
  font-weight: 600;
  flex: 1;
}

.collapse-toggle {
  margin-left: auto;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  
  i {
    font-size: 16px;
    color: #909399;
    transition: transform 0.2s ease;
  }
  
  &:hover {
    background-color: rgba(114, 69, 209, 0.1);
    
    i {
      color: #722ED1;
    }
  }
}

.topic-content {
  transition: all 0.3s ease;
}

.section {
  margin-bottom: 24px;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
}

.section-header {
  font-weight: 600;
  margin-bottom: 16px;
  font-size: 16px;
  color: #303133;
  position: relative;
  padding-left: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  &:before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 16px;
    background-color: #7245d1;
    border-radius: 2px;
  }
}

.answer-rating {
  margin-left: 10px;
}

.answer-tag {
  margin-left: 10px;
}

.section-content {
  line-height: 1.6;
  color: #606266;
}

.user-answer {
  background-color: #ffffff;
  border-color: #e4e7ed;
}

.reference-answer {
  background-color: #f3f0ff;
  border-color: #d1d5db;
}

.analysis {
  background-color: #ffffff;
  border-color: #e4e7ed;
}

.improvement {
  background-color: #f3f0ff;
  border-color: #d1d5db;
}

.analysis-strength,
.analysis-weakness {
  margin-bottom: 16px;
}

.analysis-label {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  
  &.good {
    background-color: rgba(103, 194, 58, 0.1);
    color: #67c23a;
  }
  
  &.warning {
    background-color: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
  }
}

.analysis-list,
.improvement-list {
  padding-left: 20px;
  
  li {
    margin-bottom: 8px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
}

.page-footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px dashed #e4e7ed;
}

.next-steps {
  text-align: center;
  
  p {
    margin-bottom: 16px;
    color: #606266;
    font-size: 16px;
  }
}

.steps-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.skeleton-content {
  padding: 20px;
}

@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }
  
  .topic-list {
    flex: none;
    width: 100%;
  }
  
  .steps-buttons {
    flex-direction: column;
    gap: 10px;
  }
}
</style>