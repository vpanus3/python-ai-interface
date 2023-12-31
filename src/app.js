import React, { useState, useEffect } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import io from 'socket.io-client';

// Enable Streaming or not
const streamingEnabled = true;

// Initialize Socket.IO connection
const socket = io('http://localhost:5000');  // Replace with your server's address and port

function App() {
  const [user_state, setUserState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [newTitle, setNewTitle] = useState('');

  const getUniqueId = function(){
    return Date.now().toString(36) + Math.random().toString(36).substring(2);
  }

  // Load session immediately
  useEffect(() => {
    fetch('./state')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Failed to fetch UserSession');
        }
      })
      .then(user_state => setUserState(user_state))
      .catch(error => setError(error))
      .finally(() => setLoading(false));
  }, []);

  // Set javascript handlers after rendering the view without error
  useEffect(() => {
    if (!loading && !error && user_state) {
      function setupSidebar() {
        const leftPanel = document.getElementById('left-panel');
        const appHeader = document.getElementById('app-header');
        const leftPanelButton = document.getElementById('left-panel-button-close');
        const leftPanelButtonOpen = document.getElementById('left-panel-button-open');
        const buttons = [leftPanelButton, leftPanelButtonOpen];
        
        buttons.forEach(button => {
          button.addEventListener('click', function() {
            if(leftPanel.classList.contains('panel-collapsed')) {
              leftPanel.classList.remove('panel-collapsed');
            } else {
              leftPanel.classList.add('panel-collapsed');
            }
            if(appHeader.classList.contains('panel-collapsed')) {
              appHeader.classList.remove('panel-collapsed');
            } else {
              appHeader.classList.add('panel-collapsed');
            }
          });
        });
      }
  
      function setupCreditsButton() {
        const creditsBtn = document.getElementById('show-credits-btn');
        const creditsContainer = document.getElementById('credits-container');
        const overlay = document.getElementById('credits-overlay');
  
        creditsBtn.addEventListener("click", function() {
          if (creditsContainer.style.display === "none" || !creditsContainer.style.display) {
            creditsContainer.style.display = "block";
            overlay.style.display = "block";
          } else {
            hideCredits();
          }
        });
  
        overlay.addEventListener("click", function() {
          creditsContainer.style.display = "none";
          overlay.style.display = "none";
        });
      }
  
      setupSidebar();
      setupCreditsButton();
      
    }
  }, [loading, error, user_state]);

  useEffect(() => {

    // Event handler for receiving messages
    socket.on('server_response', (data) => {
      console.log(data.message)
    });

    socket.on('user_state', (data) => {
      var json = JSON.stringify(data);
      console.log("got streaming response via websocket");
      setUserState(data);
    });

    // Event handler for connection opening
    socket.on('connect', () => {
      console.log('Socket.IO connection opened');
    });

    // Event handler for connection closing
    socket.on('disconnect', () => {
      console.log('Socket.IO connection closed');
    });

    // Cleanup function to disconnect the Socket.IO connection when the component unmounts
    return () => {
      socket.disconnect();
    };
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (streamingEnabled) {
        streamChatMessage(e);
    } else {
        sendChatMessage(e);
    }
  };

  // Handle user submitting a message
  const sendChatMessage = async (e) => {
    e.preventDefault();
  
    // Don't allow starting another message
    if (streaming) { return; }
    setStreaming(true);

    const formData = new FormData();
    formData.append('message', message);
  
    try {
      const response = await fetch('/conversation/message', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const updatedUserState = await response.json();       
        setUserState(updatedUserState);
      } else {
        throw new Error('Failed to send chat message');
      }
    } catch (err) {
      console.log(err);
      setError(err);
    } finally {
      setMessage('');
      setStreaming(false);
    }
  };

  // Handle user submitting a streaming message
  const streamChatMessage = async (e) => {
    e.preventDefault();
  
    // Don't allow starting another message
    if (streaming) { return; }
    setStreaming(true);

    const formData = new FormData();
    formData.append('message', message);
  
    try {
      const response = await fetch('/conversation/stream', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const streamResponse = await response.json();
        console.log(streamResponse.message);       
      } else {
        throw new Error('Failed to send chat message');
      }
    } catch (err) {
      console.log(err);
      setError(err);
    } finally {
      setMessage('');
      setStreaming(false);
    }
  };

  const onChatMessageChange = (e) => {
    setMessage(e.target.value);
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch('/conversation/create', {
        method: 'POST',
      });

      if (response.ok) {
        const updatedUserState = await response.json();
        setUserState(updatedUserState);
      } else {
        throw new Error('Failed to create new conversation');
      }
    } catch (error) {
      console.error(error);
    }
  };

  const switchConversation = async (conversationId) => {
    try {
      const response = await fetch(`/conversation/switch?conversation_id=${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        const updatedUserState = await response.json();
        setUserState(updatedUserState);
      } else {
        throw new Error('Failed to switch conversation');
      }
    } catch (error) {
      console.error(error);
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      const isConfirmed = window.confirm("Are you sure you want to delete this chat?");
      if (isConfirmed) {
        const response = await fetch(`/conversation/delete?conversation_id=${conversationId}`, {
          method: 'DELETE'
        });
    
        if (response.ok) {
          const updatedUserState = await response.json();
          setUserState(updatedUserState);
        } else {
          throw new Error('Failed to delete conversation');
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const stopStreaming = async (e) => {
    e.preventDefault();
    try {
      let conversationId = user_state.conversation.id
      const response = await fetch(`/conversation/stop?conversation_id=${conversationId}`, {
        method: 'POST'
      });
  
      if (response.ok) {
        const stopResponse = await response.json();
        console.log(stopResponse.message);
      } else {
        throw new Error('Failed to stop streaming');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleEdit = (conversationId, currentTitle) => {
    setEditingId(conversationId);
    setNewTitle(currentTitle);
  };

  const handleSave = async (conversationId) => {
    try {
      const response = await fetch('/conversation/rename', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          conversation_id: conversationId, 
          title: newTitle 
        }),
      });
  
      if (response.ok) {
        const updatedUserState = await response.json();
        setUserState(updatedUserState);
        setEditingId(null);
      } else {
        throw new Error('Failed to rename conversation');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopyClick = (elementId) => {
    const codeBlock = document.getElementById(elementId);
    if (codeBlock) {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(codeBlock);
      selection.removeAllRanges();
      selection.addRange(range);
      document.execCommand('copy');
      selection.removeAllRanges();
      console.log('Code copied successfully!');
    }
  };

  const formatMessage = (message) => {
    const lines = message.split('\n');
    const formattedLines = [];
    let listItems = [];
    let isCode = false;
    let codeLines = [];
    let language = null;
    
    // This regular expression will match any line that starts with ``` and capture any characters following it
    const codeBlockRegex = /^```(.*)$/;

    lines.forEach((line, index) => {
      const match = codeBlockRegex.exec(line.trim());  // Attempt to match the line against the regex
      if (match) {
        if (isCode) {
          const uniqueId = Math.random().toString(36).substring(2, 9);
          isCode = false;

          formattedLines.push(
            <div key={`code-${index}`} className="code-container">
              <div className="code-header">
                <span className="code-language">{language}</span>
                <img src="/static/flaticon-duplicate.png" alt="Copy" title="Copy Code" className="copy-code-button img-fluid" onClick={() => handleCopyClick(uniqueId)} />
              </div>
              <SyntaxHighlighter language={language} style={docco} id={uniqueId}>
                {codeLines.join('\n')}
              </SyntaxHighlighter>
            </div>
          );
          codeLines = [];
        } else {
          isCode = true;
          language = match[1] || 'plaintext';
        }
        return;
      }
  
      if (isCode) {
        codeLines.push(line);
        return;
      }
  
      if (line.startsWith("- ")) {
        listItems.push(<li key={`li-${index}`}>{line.slice(2)}</li>);
      } else {
        if (listItems.length > 0) {
          formattedLines.push(<ul key={`ul-${index}`}>{listItems}</ul>);
          listItems = [];
        }
        formattedLines.push(<p key={`p-${index}`}>{line}</p>);
      }
    });
  
    if (listItems.length > 0) {
      formattedLines.push(<ul key={`ul-last`}>{listItems}</ul>);
    }
  
    return <div className="format-message-container">{formattedLines}</div>;
  };
  

  // All useEffect statements need to precede this
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div className="container-fluid app-container">
      <div className="row app-container-row">
        <div className="col-2 d-flex flex-column left-panel" id="left-panel">
          <div className="row p-2">
            <div className="col d-flex left-panel-controls">
              <button className="btn btn-secondary flex-grow-1" onClick={createNewConversation}>+ New Conversation</button>
              <button className="btn btn-secondary ms-2 left-panel-button left-panel-button-close" id="left-panel-button-close">
                <img src="/static/flaticon-sidebar.png" alt="Sidebar" className="img-fluid" />
              </button>
            </div>
          </div>
          <div className="row p-2">
            <ol className="list-group user-conversation-list">
              {user_state.user_conversations.map((user_conversation, index) => (
                <li 
                  key={index}
                  onClick={() => switchConversation(user_conversation.conversation_id)}
                  className={
                    `user-conversation-item list-group-item text-light d-flex align-items-center justify-content-between 
                    ${user_state.conversation && user_conversation.conversation_id === user_state.conversation.id ? 'bg-active' : 'bg-secondary'}`
                  }
                >
                  <div className="d-flex align-items-center">
                    <img src="/static/flaticon-message.png" alt="Conversation" className="img-fluid me-2" />
                    {editingId === user_conversation.conversation_id ? (
                      <input 
                        type="text" 
                        value={newTitle} 
                        onChange={(e) => setNewTitle(e.target.value)}
                        onKeyDown={(e) => e.key === 'Escape' && setEditingId(null)}
                      />
                    ) : (
                      <div>{user_conversation.title || "[Untitled]"}</div>
                    )}
                  </div>
                  <div className="d-flex align-items-center">
                    {editingId === user_conversation.conversation_id ? (
                      <button className="btn btn-secondary btn-sm" onClick={() => handleSave(user_conversation.conversation_id)}>{"\u2713"}</button>
                    ) : (
                      <button className="btn btn-secondary btn-sm" onClick={() => handleEdit(user_conversation.conversation_id, user_conversation.title)}>
                        <img src="/static/flaticon-edit.png" alt="Edit" className="img-fluid" />
                      </button>
                    )}
                    <button className="btn btn-secondary btn-sm" onClick={(event) => {
                      event.stopPropagation();
                      deleteConversation(user_conversation.conversation_id);
                    }}>
                      <img src="/static/flaticon-delete.png" alt="Delete" className="img-fluid" />
                    </button>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <div className="mt-auto credits-button-container">
            <button id="show-credits-btn" className="btn btn-secondary mt-3">Credits</button>
          </div>
        </div>
        <div className="col-5 mx-auto chat-panel">
          <div className="row p-2 app-header" id="app-header">
            <h4 className="text-light">Python AI Interface</h4>
            <button className="btn btn-secondary ms-2 left-panel-button left-panel-button-open" id="left-panel-button-open">
              <img src="/static/flaticon-sidebar.png" alt="Sidebar" className="img-fluid" />
            </button>
          </div>
          <div className="row p-2">
            <div className="input-group mb-3 chat-form-container">
              <form onSubmit={handleSendMessage} className="w-100 chat-form">
                <textarea 
                  name="message" 
                  className="chat-textarea" 
                  placeholder="Send a message" 
                  required value={message} 
                  disabled={streaming}
                  onChange={onChatMessageChange}>
                </textarea>
                <button type="submit" className={`btn btn-secondary btn-chat-generate ${streaming ? 'd-none' : ''}`} disabled={streaming}>
                  <img src="/static/flaticon-right-arrow.png" alt="Send Message" className="img-fluid" />
                </button>
                <button type="button" className={`btn btn-secondary btn-chat-generate ${!streaming ? 'd-none': ''}`} disabled={!streaming} onClick={stopStreaming}>
                  <img src="/static/flaticon-close-button.png" alt="Send Message" className="img-fluid" />
                </button>
              </form>
            </div>
            <div className="chat-responses-container text-light rounded">
              {user_state && user_state.conversation ? (
                user_state.conversation.messages
                  .slice(0)
                  .reverse()
                  .map((message, index) => {
                    const formattedContent = formatMessage(message.content);
                    let imageLink="/static/flaticon-user.png"
                    let altMessage="User"
                    let className="alert alert-dark chat-message"
                    if (message.role === "assistant") {
                      imageLink="/static/flaticon-brain.png";
                      altMessage="Bot";
                      className="alert alert-secondary chat-message";
                    }
                    return (
                      <div key={index} className={className} id={message.id}>
                        <img
                          src={imageLink}
                          alt={altMessage}
                          className="message-role-image img-fluid"
                        />
                        <img src="/static/flaticon-duplicate.png" alt="Copy" tile="Copy Message" className="copy-message-button img-fluid" onClick={() => handleCopyClick(message.id)}/>
                        <span>{formattedContent}</span>
                      </div>
                    );
                  })
              ) : null}
            </div>
          </div>
        </div>
      </div>
      <div id="credits-overlay" className="credits-overlay"></div>
      <div id="credits-container" className="credits-container">
        <h2>Credits</h2>
        <div><a href="https://www.flaticon.com/free-icons/user" title="user icons">User icons created by kmg design - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/brain" title="brain icons">Brain icons created by Freepik - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/sidebar" title="sidebar icons">Sidebar icons created by Royyan Wijaya - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/edit" title="edit icons">Edit icons created by Kiranshastry - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/delete" title="delete icons">Delete icons created by Kiranshastry - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/ui" title="ui icons">Ui icons created by NajmunNahar - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/speech-bubble" title="speech bubble icons">Speech bubble icons created by Smashicons - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/duplicate" title="duplicate icons">Duplicate icons created by Erix - Flaticon</a></div>
        <div><a href="https://www.flaticon.com/free-icons/close-button" title="close button icons">Close button icons created by Ponti Project - Flaticon</a></div>
      </div>
    </div>
  )
}

export default App;