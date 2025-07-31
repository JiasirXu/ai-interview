#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并发处理、协程控制工具
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Callable, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: str = None
    start_time: float = None
    end_time: float = None
    duration: float = None

class AsyncTaskManager:
    """异步任务管理器"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._task_counter = 0
        self._lock = threading.Lock()
    
    def generate_task_id(self) -> str:
        """生成任务ID"""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter}_{int(time.time())}"
    
    async def submit_async_task(self, 
                               coro: Callable, 
                               *args, 
                               task_id: str = None,
                               **kwargs) -> str:
        """提交异步任务"""
        if task_id is None:
            task_id = self.generate_task_id()
        
        # 创建任务结果对象
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            start_time=time.time()
        )
        self.task_results[task_id] = task_result
        
        # 创建并启动任务
        task = asyncio.create_task(self._execute_async_task(coro, task_id, *args, **kwargs))
        self.tasks[task_id] = task
        
        logger.info(f"异步任务已提交: {task_id}")
        return task_id
    
    async def _execute_async_task(self, 
                                 coro: Callable, 
                                 task_id: str,
                                 *args, 
                                 **kwargs):
        """执行异步任务"""
        task_result = self.task_results[task_id]
        
        try:
            task_result.status = TaskStatus.RUNNING
            logger.info(f"异步任务开始执行: {task_id}")
            
            # 执行协程
            if asyncio.iscoroutinefunction(coro):
                result = await coro(*args, **kwargs)
            else:
                result = coro(*args, **kwargs)
            
            task_result.result = result
            task_result.status = TaskStatus.COMPLETED
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
            logger.info(f"异步任务执行完成: {task_id}, 耗时: {task_result.duration:.2f}s")
            
        except asyncio.CancelledError:
            task_result.status = TaskStatus.CANCELLED
            task_result.error = "任务被取消"
            logger.warning(f"异步任务被取消: {task_id}")
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            logger.error(f"异步任务执行失败: {task_id}, 错误: {e}")
        
        finally:
            # 清理任务
            if task_id in self.tasks:
                del self.tasks[task_id]
    
    def submit_sync_task(self, 
                        func: Callable, 
                        *args, 
                        task_id: str = None,
                        **kwargs) -> str:
        """提交同步任务到线程池"""
        if task_id is None:
            task_id = self.generate_task_id()
        
        # 创建任务结果对象
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatus.PENDING,
            start_time=time.time()
        )
        self.task_results[task_id] = task_result
        
        # 提交到线程池
        future = self.executor.submit(self._execute_sync_task, func, task_id, *args, **kwargs)
        
        logger.info(f"同步任务已提交: {task_id}")
        return task_id
    
    def _execute_sync_task(self, 
                          func: Callable, 
                          task_id: str,
                          *args, 
                          **kwargs):
        """执行同步任务"""
        task_result = self.task_results[task_id]
        
        try:
            task_result.status = TaskStatus.RUNNING
            logger.info(f"同步任务开始执行: {task_id}")
            
            result = func(*args, **kwargs)
            
            task_result.result = result
            task_result.status = TaskStatus.COMPLETED
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            
            logger.info(f"同步任务执行完成: {task_id}, 耗时: {task_result.duration:.2f}s")
            
        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.end_time = time.time()
            task_result.duration = task_result.end_time - task_result.start_time
            logger.error(f"同步任务执行失败: {task_id}, 错误: {e}")
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> TaskResult:
        """等待任务完成"""
        if task_id not in self.task_results:
            raise ValueError(f"任务不存在: {task_id}")
        
        start_time = time.time()
        while True:
            task_result = self.task_results[task_id]
            
            if task_result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return task_result
            
            if timeout and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError(f"等待任务超时: {task_id}")
            
            await asyncio.sleep(0.1)
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """获取任务状态"""
        return self.task_results.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.cancel()
            return True
        return False
    
    def get_all_tasks(self) -> Dict[str, TaskResult]:
        """获取所有任务状态"""
        return self.task_results.copy()
    
    def clear_completed_tasks(self):
        """清理已完成的任务"""
        completed_tasks = [
            task_id for task_id, result in self.task_results.items()
            if result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        
        for task_id in completed_tasks:
            del self.task_results[task_id]
        
        logger.info(f"已清理 {len(completed_tasks)} 个完成的任务")
    
    def shutdown(self):
        """关闭任务管理器"""
        # 取消所有待处理的任务
        for task_id, task in self.tasks.items():
            task.cancel()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        logger.info("任务管理器已关闭")


class ConcurrentExecutor:
    """并发执行器"""
    
    @staticmethod
    async def gather_with_concurrency(limit: int, *coros) -> List[Any]:
        """限制并发数量的gather"""
        semaphore = asyncio.Semaphore(limit)
        
        async def limited_coro(coro):
            async with semaphore:
                return await coro
        
        limited_coros = [limited_coro(coro) for coro in coros]
        return await asyncio.gather(*limited_coros, return_exceptions=True)
    
    @staticmethod
    async def execute_with_timeout(coro, timeout: float):
        """带超时的协程执行"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"协程执行超时: {timeout}s")
            raise
    
    @staticmethod
    async def retry_async(coro: Callable, 
                         max_retries: int = 3, 
                         delay: float = 1.0,
                         backoff: float = 2.0) -> Any:
        """异步重试机制"""
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(coro):
                    return await coro()
                else:
                    return coro()
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"重试失败，已达到最大重试次数: {max_retries}")
                    raise
                
                wait_time = delay * (backoff ** attempt)
                logger.warning(f"执行失败，{wait_time:.2f}s后重试 (第{attempt + 1}次): {e}")
                await asyncio.sleep(wait_time)


class InterviewSession:
    """面试会话"""
    
    def __init__(self, user_id: int, interview_id: int, services: Dict[str, Any]):
        self.user_id = user_id
        self.interview_id = interview_id
        self.services = services
        self.status = 'created'

class InterviewSessionManager:
    """面试会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.sid_to_session: Dict[str, str] = {}
        self.task_manager = AsyncTaskManager(max_workers=10)
        self._lock = threading.Lock()  # 添加线程锁
    
    def create_session(self, 
                      user_id: int, 
                      interview_id: int, 
                      services: Dict[str, Any]) -> str:
        """创建面试会话"""
        session_id = f"session_{interview_id}_{user_id}"
        
        # 使用线程锁确保会话创建的线程安全
        with self._lock:
            if session_id in self.sessions:
                logger.warning(f"会话 {session_id} 已存在，将重新创建")
                # 可选择在这里清理旧会话
            
            self.sessions[session_id] = {
                'user_id': user_id,
                'interview_id': interview_id,
                'services': services,
                'status': 'created',
                'started_at': time.time(),
                'context': {}  # 添加context字典
            }
            logger.info(f"面试会话已创建: {session_id}, 用户ID: {user_id}")
        
        return session_id
        
    def end_session(self, session_id: str) -> bool:
        """结束面试会话"""
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'ended'
            self.sessions[session_id]['ended_at'] = time.time()
            
            logger.info(f"面试会话已结束: {session_id}")
            return True
        return False
    
    def cleanup_session(self, session_id: str):
        """清理会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        sids_to_remove = [sid for sid, s_id in self.sid_to_session.items() if s_id == session_id]
        for sid in sids_to_remove:
            if sid in self.sid_to_session:
                del self.sid_to_session[sid]
                logger.info(f"SID {sid} 的关联已移除")

        logger.info(f"面试会话已清理: {session_id}")
    
    async def register_sid(self, session_id: str, sid: str):
        """将会话ID与Socket.IO的SID关联"""
        self.sid_to_session[sid] = session_id
        logger.info(f"SID {sid} 已注册到会话 {session_id}")

    def get_session_by_sid(self, sid: str) -> Optional[str]:
        """通过SID获取会话ID"""
        return self.sid_to_session.get(sid)

    async def execute_concurrent_services(self, 
                                        session_id: str, 
                                        service_calls: List[Tuple[str, Callable, tuple, dict]]) -> Dict[str, Any]:
        """并发执行多个服务调用"""
        results = {}
        for name, func, args, kwargs in service_calls:
            results[name] = await self.task_manager.submit_async_task(func, *args, **kwargs)
        
        # 等待所有任务完成
        for task_id in results:
            try:
                task_result = await self.task_manager.wait_for_task(task_id)
                results[task_id] = task_result
            except asyncio.TimeoutError:
                logger.warning(f"服务调用超时: {task_id}")
                results[task_id] = TaskResult(task_id, TaskStatus.FAILED, error="服务调用超时")
            except Exception as e:
                logger.error(f"服务调用失败: {task_id}, 错误: {e}")
                results[task_id] = TaskResult(task_id, TaskStatus.FAILED, error=str(e))
        
        return results

    def get_all_sessions(self) -> Dict[str, Any]:
        """获取所有会话的状态"""
        return {
            session_id: session
            for session_id, session in self.sessions.items()
        } 

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """通过会话ID获取会话"""
        return self.sessions.get(session_id)

# 创建一个全局唯一的会话管理器实例
interview_manager = InterviewSessionManager() 