#include <stack>
#include <iostream>
#include <thread>
#include <string>
#include <fstream>
#include <atomic>
#include <mutex>
#include <vector>
typedef unsigned char UINT8;
const int INVALID_STACK_ID = 255;
const int MAX_STACK_ID = 254;
const int MAX_STACK_NUMBER = 255;
template<typename T>
class ObjectPool
{
public:
    ObjectPool()
    {
        m_dwStackSize = 0;
        m_dwThreadCount = 0;
        m_dwAllocSize = 0;
        m_dwFreeSize = 0;
        for (int i = 0; i < MAX_STACK_NUMBER; i++)
        {
            m_oAllObjs[i] = nullptr;
        }
    }
    ~ObjectPool()
    {
        //删除所有,主线程负责析构，必须保证使用线程都已停止
        for (int i = 0; i < MAX_STACK_NUMBER; i++)
        {
            if (m_oAllObjs[i] != nullptr)
            {
                delete[] m_oAllObjs[i];
                std::cout << "delete obj[" << i << "] OK" << std::endl;
                m_oAllObjs[i] = nullptr;
            }
        }
        std::cout << " done!" << std::endl;
    }
    //指定栈大小，指定线程数
    void Init(int _stack_size, int _thread_count)
    {
        m_dwStackSize = _stack_size;
        m_dwThreadCount = _thread_count;
        for (int i = 0; i < m_dwThreadCount; i++)
        {
            m_oAllObjs[i] = new shellT[m_dwStackSize];
            for (int j = 0; j < m_dwStackSize; j++)
            {
                m_oAllObjs[i][j]._stack_id = i;
                m_oFreeIndex[i]._object_stack.push(&m_oAllObjs[i][j]);
            }
        }
    }
    //给每个线程调用，校正计数器的函数
    void Debug_Init()
    {
        m_dwFreeSize += m_dwStackSize;
    }
    //设置线程索引
    void SetThreadIndex(int idx)
    {
        m_dwThreadIndex = idx;
        std::string file = "out" + std::to_string(idx) + ".txt";
        //m_ofs.open(file, std::ios::out);
    }
    T* FetchObj()
    {
        return _fetch_obj(m_dwThreadIndex);
    }
    T* _fetch_obj(int _cur_stack_id)
    {
        FreeStack* head = &m_oFreeIndex[_cur_stack_id];
        if (!head->_object_stack.empty())
        {
            T* ret = head->_object_stack.top();
            head->_object_stack.pop();
            
            m_dwFreeSize--;
            m_dwAllocSize++;
            //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " alloc size[" << m_dwAllocSize << "] free size[" << m_dwFreeSize << "]\n";
            return ret;
        }
        if (head->_next_stack_id != INVALID_STACK_ID)
        {
            return _fetch_obj(head->_next_stack_id);
        }
        if (_AllocT(_cur_stack_id))
        {
            return _fetch_obj(head->_next_stack_id);
        }
        return nullptr;
    }
    void ReleaseObj(T* pObj)
    {
        if (pObj == nullptr)return;
        //如果栈满，释放栈
        shellT* ptr = static_cast<shellT*>(pObj);
        int _stack_id = ptr->_stack_id;
        auto& _stack = m_oFreeIndex[_stack_id]._object_stack;
        _stack.push(ptr);
        
        m_dwFreeSize++;
        m_dwAllocSize--;
        //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " alloc size[" << m_dwAllocSize << "] free size[" << m_dwFreeSize << "]\n";
        if (_stack.size()==m_dwStackSize && _stack_id >= m_dwThreadCount)
        {
            int _prev_id = m_oFreeIndex[_stack_id]._prev_stack_id;
            int _next_id = m_oFreeIndex[_stack_id]._next_stack_id;
            m_oFreeIndex[_prev_id]._next_stack_id = _next_id;
            m_oFreeIndex[_next_id]._prev_stack_id = _prev_id;
            m_oFreeIndex[_stack_id].reset();
            delete[] m_oAllObjs[_stack_id];
            m_oAllObjs[_stack_id] = nullptr;
            m_dwFreeSize -= m_dwStackSize;
            //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " delete stack[" << _stack_id << "]\n";
            //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " alloc size[" << m_dwAllocSize << "] free size[" << m_dwFreeSize << "]\n";
        }
    }
protected:
    bool _AllocT(int _last_id)
    {
        int _id = _alloc_id();
        if (_id != INVALID_STACK_ID)
        {
            shellT* p = m_oAllObjs[_id];
            m_oFreeIndex[_last_id]._next_stack_id = _id;
            m_oFreeIndex[_id]._prev_stack_id = _last_id;
            for (int j = 0; j < m_dwStackSize; j++)
            {
                p[j]._stack_id = _id;
                m_oFreeIndex[_id]._object_stack.push(&p[j]);
            }
            m_dwFreeSize += m_dwStackSize;
            //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " new stack[" << _id << "]\n";
            //m_ofs << "--" << m_dwThreadIndex << "--" << __FUNCTION__ << " alloc size[" << m_dwAllocSize << "] free size[" << m_dwFreeSize << "]\n";
            return true;
        }
        return false;
    }
    int _alloc_id()
    {
        //如果栈不空就是被占用的
        std::unique_lock<std::mutex> locker(m_alloc_mutex);
        for (int i = m_dwThreadCount; i < MAX_STACK_NUMBER; i++)
        {
            if (m_oAllObjs[i] == nullptr)
            {
                m_oAllObjs[i] = new shellT[m_dwStackSize];
                return i;
            }
        }
        return INVALID_STACK_ID;
    }
protected:
    //对象加壳，增加栈地址，用来回收
    struct shellT : public T
    {
        UINT8 _stack_id = INVALID_STACK_ID;//栈id (0~254)
    };
    struct FreeStack //空闲指针栈
    {
        FreeStack() :_prev_stack_id(INVALID_STACK_ID), _next_stack_id(INVALID_STACK_ID)
        {
        }
        UINT8 _prev_stack_id ;//上一个栈id
        UINT8 _next_stack_id ;//下一个栈id
        std::stack<shellT*> _object_stack;
        void reset()
        {
            _prev_stack_id = INVALID_STACK_ID;
            _next_stack_id = INVALID_STACK_ID;
            //_object_stack.swap(std::stack<shellT*>());
        }
    };
    std::mutex m_alloc_mutex;//alloc时需要互斥
    int m_dwStackSize;//栈大小
    int m_dwThreadCount;//线程数 （0~count-1的栈是固定分配的 count~254 的栈是动态分配的）
    shellT* m_oAllObjs[MAX_STACK_NUMBER];//全部栈空间
    FreeStack m_oFreeIndex[MAX_STACK_NUMBER];//全部栈空间的空闲对象栈索引
public:
    thread_local static int m_dwThreadIndex;//线程索引
    //thread_local static std::ofstream m_ofs;//输出文件流
    thread_local static int m_dwAllocSize;
    thread_local static int m_dwFreeSize;
};
struct MyObj
{
    MyObj()
    {
        m_idx = 0;
        m_value = 0;
    }
    void init(int idx, int val)
    {
        //ObjectPool<MyObj>::m_ofs << "thread index = " << idx << " value = " << val << std::endl;
    }
private:
    int m_idx;
    int m_value;
};
template<> thread_local int ObjectPool<MyObj>::m_dwThreadIndex = 0;
//template<> thread_local std::ofstream ObjectPool<MyObj>::m_ofs;
template<> thread_local int ObjectPool<MyObj>::m_dwAllocSize = 0;
template<> thread_local int ObjectPool<MyObj>::m_dwFreeSize = 0;
ObjectPool<MyObj> obj_pool;
const int thread_count = 5;
const int thread_obj_count = 100;
