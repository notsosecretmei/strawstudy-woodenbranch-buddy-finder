// Show a simple temporary notification
function showNotification(message) {
  const bar = document.getElementById('notification');
  bar.innerText = message;
  bar.style.display = 'block';

  // Hide after 3 seconds
  setTimeout(() => {
    bar.style.display = 'none';
  }, 3000);
}

// Example: call showNotification("Buddy request sent!") when a request is sent
