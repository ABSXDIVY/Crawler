/* global fetch, TextDecoder */
(function () {
  const state = {
    controller: null,
    latestText: "",
  };

  // Elements
  const el = {
    form: document.querySelector('#searchForm'),
    query: document.querySelector('#query'),
    status: document.querySelector('#status'),
    output: document.querySelector('#output'),
    log: document.querySelector('#log'),
    cancel: document.querySelector('#cancelBtn'),
    copyBtn: document.querySelector('#copyBtn'),
  };

  // 固定配置 - 使用本地代理避免CORS
  const CONFIG = {
    baseUrl: 'http://localhost:8000/proxy',  // 通过本地代理
    apiKey: 'application-ad6838518159e632447b68bfc3cbdf6a',
    csrfToken: 'BVENCq9RviQSMG0gG6UC8Yxustm5JzA0LsdgQIomrieUN1hWrtWTGkqv7tSvkkQU',
  };

  el.copyBtn.addEventListener('click', async () => {
    if (!state.latestText) return;
    try {
      await navigator.clipboard.writeText(state.latestText);
      toast('已复制到剪贴板');
    } catch {
      toast('复制失败');
    }
  });

  el.cancel.addEventListener('click', () => {
    if (state.controller) {
      state.controller.abort();
      state.controller = null;
      setStatus('已取消');
    }
  });

  el.form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = el.query.value.trim();
    if (!message) return;

    resetOutput();
    setStatus('打开会话...');

    try {
      // 1) open chat
      const openUrl = `${CONFIG.baseUrl}/open`;
      const openHeaders = {
        'accept': 'application/json',
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'X-CSRFTOKEN': CONFIG.csrfToken,
      };

      state.controller = new AbortController();
      const openResp = await fetch(openUrl, {
        method: 'GET',
        headers: openHeaders,
        signal: state.controller.signal,
      });
      
      if (!openResp.ok) throw new Error('open 失败: ' + openResp.status);
      const openData = await openResp.json();
      const chatId = openData.data;
      if (!chatId) throw new Error('未返回 chat_id');

      // 2) send message
      const msgUrl = `${CONFIG.baseUrl}/chat_message/${chatId}`;
      const payload = {
        message,
        stream: true,
        re_chat: false,
        image_list: [],
        document_list: [],
        audio_list: [],
        video_list: [],
        other_list: [],
        form_data: {}
      };
      
      const postHeaders = {
        'accept': '*/*',
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': CONFIG.csrfToken,
      };

      setStatus('等待回复...');
      await doStream(msgUrl, postHeaders, payload);
      setStatus('完成');
    } catch (err) {
      setStatus('错误');
      logLine('Error: ' + (err?.message || String(err)));
    } finally {
      state.controller = null;
    }
  });

  async function doStream(url, headers, body) {
    const controller = (state.controller = new AbortController());
    const resp = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    
    if (!resp.ok) {
      const t = await resp.text();
      logLine(`[stream] status=${resp.status} body=${t}`);
      throw new Error('HTTP ' + resp.status);
    }
    
    const reader = resp.body.getReader();
    const decoder = new TextDecoder('utf-8');
    setStatus('流式接收中...');
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      for (const line of chunk.split(/\r?\n/)) {
        if (!line) continue;
        if (!line.startsWith('data:')) continue;
        
        const dataStr = line.slice(5).trim();
        if (!dataStr) continue;
        
        try {
          const obj = JSON.parse(dataStr);
          const content = obj?.content;
          if (typeof content === 'string') appendOutput(content);
        } catch {
          // ignore non-JSON
        }
      }
    }
  }

  function resetOutput() {
    el.output.textContent = '';
    state.latestText = '';
    el.log.textContent = '';
  }
  
  function appendOutput(text) {
    state.latestText += text;
    el.output.textContent = state.latestText;
  }
  
  function setStatus(text) { 
    el.status.textContent = text; 
  }
  
  function logLine(text) { 
    el.log.textContent += text + '\n'; 
  }
  
  function toast(text) {
    setStatus(text);
    setTimeout(() => setStatus('就绪'), 1500);
  }
})();


