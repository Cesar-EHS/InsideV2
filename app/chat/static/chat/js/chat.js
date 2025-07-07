// Chat Widget JS
let chatWidget, chatFab, chatClose, chatUsers, chatMessages, chatInput, chatSend;
document.addEventListener('DOMContentLoaded', function() {
  chatWidget = document.getElementById('chat-widget');
  chatFab = document.getElementById('chat-fab');
  chatClose = document.getElementById('chat-close');
  chatUsers = document.getElementById('chat-users');
  chatMessages = document.getElementById('chat-messages');
  chatInput = document.getElementById('chat-input');
  chatSend = document.getElementById('chat-send');

  if(chatFab) chatFab.onclick = () => { chatWidget.style.display = 'flex'; chatFab.style.display = 'none'; loadUsers(); };
  if(chatClose) chatClose.onclick = () => { chatWidget.style.display = 'none'; chatFab.style.display = 'flex'; };
  if(chatSend) chatSend.onclick = sendMessage;
  if(chatInput) chatInput.addEventListener('keydown', function(e){ if(e.key==='Enter'){ sendMessage(); }});
});

let currentConversationId = null;
let currentUserId = null;

function loadUsers() {
  fetch('/chat/list_users').then(r=>r.json()).then(users => {
    chatUsers.innerHTML = '';
    users.forEach(u => {
      const btn = document.createElement('button');
      btn.className = 'w-full flex flex-col items-center py-2 hover:bg-inside-yellow/30 transition';
      btn.innerHTML = `<img src="${u.foto||'/static/img/user.png'}" class="w-8 h-8 rounded-full mb-1"><span class="text-xs text-inside-blue font-sfpro">${u.nombre}</span>`;
      btn.onclick = () => loadConversation(u.id);
      chatUsers.appendChild(btn);
    });
  });
}

function loadConversation(userId) {
  fetch(`/chat/conversation/${userId}`).then(r=>r.json()).then(data => {
    currentConversationId = data.conversation_id;
    currentUserId = userId;
    chatMessages.innerHTML = '';
    data.messages.forEach(m => {
      const isMine = m.sender_id === window.currentUserId;
      const div = document.createElement('div');
      div.className = 'flex flex-col mb-1 ' + (isMine ? 'items-end' : 'items-start');
      div.innerHTML = `<div class="rounded-xl px-3 py-2 ${isMine ? 'bg-inside-yellow text-inside-blue' : 'bg-inside-blue text-white'} max-w-xs font-sfpro">${m.content||''}</div><span class="text-xs text-gray-400 mt-1">${m.timestamp}</span>`;
      chatMessages.appendChild(div);
    });
    chatMessages.scrollTop = chatMessages.scrollHeight;
  });
}

function sendMessage() {
  if(!chatInput.value.trim() || !currentConversationId) return;
  const form = new FormData();
  form.append('conversation_id', currentConversationId);
  form.append('message', chatInput.value);
  fetch('/chat/send', {method:'POST', body:form}).then(r=>r.json()).then(resp => {
    if(resp.status==='ok'){
      loadConversation(currentUserId);
      chatInput.value = '';
    }
  });
}
