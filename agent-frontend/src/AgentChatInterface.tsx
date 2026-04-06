import React, { useState, useRef } from 'react';

const AgentChatInterface: React.FC = () => {
  // --- State 管理 ---
  const [query, setQuery] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [finalAnswer, setFinalAnswer] = useState('');
  const [toolSteps, setToolSteps] = useState<ToolStep[]>([]);
  const [systemStatus, setSystemStatus] = useState<string | null>(null);

  // 避免重複請求的防呆機制
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleAskAgent = async () => {
    if (!query) return;

    // 初始化狀態
    setIsStreaming(true);
    setFinalAnswer('');
    setToolSteps([]);
    setSystemStatus('連線中...');

    abortControllerRef.current = new AbortController();

    try {
      // 這裡使用 GET 作為範例，實際 AI 應用常改為 POST
      const response = await fetch(`http://127.0.0.1:8000/api/chat/stream?query=${encodeURIComponent(query)}`, {
        method: 'GET',
        signal: abortControllerRef.current.signal,
        headers: {
          'Accept': 'text/event-stream',
        },
      });

      if (!response.body) throw new Error('ReadableStream not supported in this browser.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = ''; // 緩衝區：用來處理被截斷的 TCP Chunk

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // 將這包 chunk 解碼為字串並加入緩衝區
        buffer += decoder.decode(value, { stream: true });

        // SSE 規範中，事件之間以雙換行符號分隔
        const parts = buffer.split('\n\n');

        // 將最後一個不完整的片段留到下一次迴圈處理！(這是最關鍵的避坑技巧)
        buffer = parts.pop() || '';

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const jsonStr = part.slice(6); // 移除 'data: ' 前綴
            if (jsonStr === '[DONE]') continue; // 常見的結束標記

            try {
              const payload = JSON.parse(jsonStr) as SSEPayload;
              handleAgentEvent(payload);
            } catch (err) {
              console.error('JSON 解析錯誤，可能封包損毀:', err, '原始字串:', jsonStr);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('使用者手動中斷連線');
      } else {
        setSystemStatus(`發生錯誤: ${error.message}`);
      }
    } finally {
      setIsStreaming(false);
      setSystemStatus(null);
    }
  };

  // --- 事件路由分發 (Event Router) ---
  const handleAgentEvent = (payload: SSEPayload) => {
    switch (payload.event) {
      case 'status':
        setSystemStatus(payload.data as string);
        break;

      case 'tool_start':
        setToolSteps((prev) => [
          ...prev,
          {
            id: Date.now().toString(), // 簡單產生 ID，實務上建議由後端提供 step_id
            toolName: payload.data.tool,
            status: 'running',
            input: payload.data.input,
          },
        ]);
        break;

      case 'tool_end':
        setToolSteps((prev) => {
          const newSteps = [...prev];
          // 找到最後一個且同名的正在執行的工具，將其狀態更新為 completed
          const lastToolIndex = newSteps.map(s => s.toolName).lastIndexOf(payload.data.tool);
          if (lastToolIndex !== -1) {
            newSteps[lastToolIndex] = {
              ...newSteps[lastToolIndex],
              status: 'completed',
              result: payload.data.result,
            };
          }
          return newSteps;
        });
        break;

      case 'content_chunk':
        // 將文字碎片接上 (打字機效果)
        setFinalAnswer((prev) => prev + (payload.data as string));
        break;

      case 'error':
        setSystemStatus(`系統異常: ${payload.data}`);
        setIsStreaming(false);
        abortControllerRef.current?.abort(); // 中斷請求
        break;

      default:
        console.warn('收到未知的 Event Type:', payload.event);
    }
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    setIsStreaming(false);
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {/* 輸入區 */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="請輸入機台分析問題..."
          style={{ flex: 1, padding: '8px' }}
        />
        {!isStreaming ? (
          <button onClick={handleAskAgent} disabled={!query}>送出</button>
        ) : (
          <button onClick={handleStop} style={{ background: '#ff4d4f', color: 'white' }}>停止</button>
        )}
      </div>

      {/* 狀態指示器 */}
      {systemStatus && (
        <div style={{ color: '#1890ff', marginBottom: '10px' }}>
          {systemStatus}
        </div>
      )}

      {/* 工具執行過程 (Reasoning Steps) */}
      {toolSteps.length > 0 && (
        <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
          <h4>🧠 Agent 思考過程</h4>
          <ul style={{ listStyleType: 'none', padding: 0 }}>
            {toolSteps.map((step, idx) => (
              <li key={step.id || idx} style={{ marginBottom: '10px' }}>
                <strong>
                  {step.status === 'running' ? '🔄 執行中: ' : '✅ 已完成: '}
                  {step.toolName}
                </strong>
                <div style={{ fontSize: '0.9em', color: '#666', marginLeft: '20px' }}>
                  {step.input && <div>輸入參數: {step.input}</div>}
                  {step.result && <div>取得結果: {step.result}</div>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 最終解答 (打字機效果) */}
      {finalAnswer && (
        <div style={{ padding: '20px', border: '1px solid #d9d9d9', borderRadius: '8px', whiteSpace: 'pre-wrap' }}>
          {finalAnswer}
        </div>
      )}
    </div>
  );
};

export default AgentChatInterface;