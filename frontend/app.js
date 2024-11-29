// 搜索邮件按钮点击事件
document.getElementById('search').addEventListener('click', async () => {
    const sender = document.getElementById('sender').value;
    const maxResults = document.getElementById('maxResults').value;
  
    // 查询邮件
    const response = await fetch('http://127.0.0.1:5000/api/search_emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender_email: sender, max_results: maxResults })
    });
  
    const emails = await response.json();
    if (response.ok) {
      displayEmails(emails);
    } else {
      alert(emails.error);
    }
  });
  
  // 显示邮件到页面（默认折叠）
  function displayEmails(emails) {
    const emailsDiv = document.getElementById('emails');
    emailsDiv.innerHTML = '';
    emails.forEach((email, index) => {
      const emailDiv = document.createElement('div');
      emailDiv.className = 'email'; // 给每封邮件一个 class，方便收集数据
      
      // 初始折叠部分内容
      emailDiv.innerHTML = `
        <h3>Email ${index + 1}</h3>
        <p><strong>Subject:</strong> ${email.subject}</p>
        <p><strong>Sender:</strong> ${email.sender}</p>
        <p><strong>Body:</strong> <span class="body-preview">${email.body.slice(0, 100)}...</span></p>
        <button class="show-full">显示全部</button>
        <div class="full-body" style="display: none;">
          <p>${email.body}</p>
        </div>
      `;
  
      // 添加到页面
      emailsDiv.appendChild(emailDiv);
  
      // 为“显示全部”按钮添加事件监听器
      emailDiv.querySelector('.show-full').addEventListener('click', () => {
        const fullBody = emailDiv.querySelector('.full-body');
        const bodyPreview = emailDiv.querySelector('.body-preview');
        const showButton = emailDiv.querySelector('.show-full');
        if (fullBody.style.display === 'none') {
          // 展开完整内容
          fullBody.style.display = 'block';
          bodyPreview.style.display = 'none';
          showButton.textContent = '折叠内容';
        } else {
          // 折叠回预览内容
          fullBody.style.display = 'none';
          bodyPreview.style.display = 'inline';
          showButton.textContent = '显示全部';
        }
      });
    });
  }
  
  // 总结邮件按钮点击事件
  document.getElementById('summarize').addEventListener('click', async () => {
    const emails = document.querySelectorAll('.email'); // 获取页面上的所有邮件
    const subjects = [];
    const bodies = [];
    const senders = [];
  
    // 收集每封邮件的主题、正文和发件人信息
    emails.forEach(email => {
      const subject = email.querySelector('p:nth-child(2)').textContent.replace('Subject:', '').trim();
      const body = email.querySelector('.full-body p').textContent;
      const sender = email.querySelector('p:nth-child(3)').textContent.replace('Sender:', '').trim();
  
      subjects.push(subject);
      bodies.push(body);
      senders.push(sender);
    });
  
    // 调用总结接口
    const response = await fetch('http://127.0.0.1:5000/api/summarize_emails', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subjects, bodies, senders })
    });
  
    const summaryData = await response.json();
    if (response.ok) {
      displaySummary(summaryData.summary);
    } else {
      alert('Error generating summary.');
    }
  });
  
  // 显示总结到页面，并渲染 Markdown
  function displaySummary(summary) {
    const summaryContent = document.getElementById('summaryContent');
    // 使用 marked.js 将 Markdown 转换为 HTML
    summaryContent.innerHTML = marked.parse(summary);
  }