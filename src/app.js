import React, { useState, useEffect } from 'react';

function App() {
  const [user_session, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('./session')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Failed to fetch UserSession');
        }
      })
      .then(user_session => setData(user_session))
      .catch(error => setError(error))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!loading && !error && user_session) {
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
  }, [loading, error, user_session]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  

  return (
    <div className="container-fluid app-container">
      <div className="row">
        <div className="col-2 d-flex flex-column left-panel" id="left-panel">
          <div className="row p-2">
            <div className="col d-flex left-panel-controls">
              <button className="btn btn-secondary flex-grow-1">+ New Conversation</button>
              <button className="btn btn-secondary ms-2 left-panel-button left-panel-button-close" id="left-panel-button-close">
                <img src="/static/flaticon-sidebar.png" alt="Sidebar" className="img-fluid" />
              </button>
            </div>
          </div>
          <div className="row p-2">
            <ol className="list-group user-conversation-list">
              {user_session.user_conversations.map((user_conversation, index) => (
                <li key={index} className="user-conversation-item list-group-item bg-secondary text-light d-flex align-items-center justify-content-between">
                  <div className="d-flex align-items-center">
                    <img src="/static/flaticon-message.png" alt="Conversation" className="img-fluid me-2" />
                    <div>{user_conversation.title}</div>
                  </div>
                  <div className="d-flex align-items-center">
                    <button className="btn btn-secondary btn-sm"><img src="/static/flaticon-edit.png" alt="Edit" className="img-fluid" /></button>
                    <button className="btn btn-secondary btn-sm"><img src="/static/flaticon-delete.png" alt="Delete" className="img-fluid" /></button>
                  </div>
                </li>
              ))}
            </ol>
          </div>
          <div className="mt-auto credits-button-container">
            <button id="show-credits-btn" className="btn btn-secondary mt-3">Credits</button>
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
              <form action="/conversation" method="post" className="w-100 chat-form">
                <textarea name="message" className="chat-textarea" placeholder="Send a message" required></textarea>
                <button type="submit" className="btn btn-secondary btn-chat-generate" id="btn-chat-generate">
                  <img src="/static/flaticon-right-arrow.png" alt="Send Message" className="img-fluid" />
                </button>
              </form>
            </div>
            <div className="chat-responses-container text-light rounded">
              {user_session && user_session.conversation ? (
                user_session.conversation.messages
                  .slice(0)
                  .reverse()
                  .map((message, index) => {
                    if (message.role === "assistant") {
                      return (
                        <div key={index} className="alert alert-secondary chat-message">
                          <img
                            src="/static/flaticon-brain.png"
                            alt="Bot"
                            className="img-fluid"
                          />
                          <span>{message.content}</span>
                        </div>
                      );
                    } else if (message.role === "user") {
                      return (
                        <div key={index} className="alert alert-dark chat-message">
                          <img
                            src="/static/flaticon-user.png"
                            alt="User"
                            className="img-fluid"
                          />
                          <span>{message.content}</span>
                        </div>
                      );
                    }
                    return null; // or you can return an empty fragment <> </>
                  })
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App;