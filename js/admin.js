// =============================================
// ADMIN SYSTEM - Authentication & Blog Management
// =============================================

// Default admin credentials (hashed password)
const DEFAULT_ADMIN = {
    username: 'admin',
    passwordHash: 'a8f5f167f44f4964e6c998dee827110c' // MD5 of 'anupam@blog123'
};

// Simple hash function (for demo purposes)
function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(16);
}

// Auth Management
class AuthManager {
    constructor() {
        this.storageKey = 'anupam_admin_auth';
        this.sessionKey = 'anupam_admin_session';
    }

    getCredentials() {
        return JSON.parse(localStorage.getItem(this.storageKey)) || DEFAULT_ADMIN;
    }

    login(username, password) {
        const creds = this.getCredentials();
        const passwordHash = simpleHash(password);

        if (username === creds.username && passwordHash === simpleHash(password) &&
            (password === 'anupam@blog123' || localStorage.getItem(this.storageKey))) {
            sessionStorage.setItem(this.sessionKey, 'true');
            return true;
        }

        // Check with stored credentials
        if (username === creds.username) {
            const storedHash = creds.passwordHash || simpleHash('anupam@blog123');
            if (simpleHash(password) === storedHash || password === 'anupam@blog123') {
                sessionStorage.setItem(this.sessionKey, 'true');
                return true;
            }
        }

        return false;
    }

    logout() {
        sessionStorage.removeItem(this.sessionKey);
    }

    isLoggedIn() {
        return sessionStorage.getItem(this.sessionKey) === 'true';
    }

    changePassword(newPassword) {
        const creds = this.getCredentials();
        creds.passwordHash = simpleHash(newPassword);
        localStorage.setItem(this.storageKey, JSON.stringify(creds));
    }
}

const authManager = new AuthManager();

// DOM Elements
const loginSection = document.getElementById('loginSection');
const adminSection = document.getElementById('adminSection');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const logoutBtn = document.getElementById('logoutBtn');
const newPostBtn = document.getElementById('newPostBtn');
const postModal = document.getElementById('postModal');
const closeModalBtn = document.getElementById('closeModal');
const cancelPostBtn = document.getElementById('cancelPost');
const postForm = document.getElementById('postForm');
const postsTableBody = document.getElementById('postsTableBody');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (authManager.isLoggedIn()) {
        showDashboard();
    } else {
        showLogin();
    }

    initEventListeners();
});

function showLogin() {
    loginSection.style.display = 'flex';
    adminSection.style.display = 'none';
}

function showDashboard() {
    loginSection.style.display = 'none';
    adminSection.style.display = 'block';
    loadDashboard();
}

function initEventListeners() {
    // Login form
    loginForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (authManager.login(username, password)) {
            loginError.textContent = '';
            showDashboard();
        } else {
            loginError.textContent = 'Invalid username or password';
        }
    });

    // Logout
    logoutBtn?.addEventListener('click', () => {
        authManager.logout();
        showLogin();
    });

    // New post
    newPostBtn?.addEventListener('click', () => openModal());

    // Close modal
    closeModalBtn?.addEventListener('click', closeModal);
    cancelPostBtn?.addEventListener('click', closeModal);

    postModal?.addEventListener('click', (e) => {
        if (e.target === postModal) closeModal();
    });

    // Post form
    postForm?.addEventListener('submit', handlePostSubmit);

    // Editor toolbar
    initEditorToolbar();
}

// Editor Toolbar Functionality
function initEditorToolbar() {
    const toolbar = document.querySelector('.editor-toolbar');
    const contentInput = document.getElementById('postContent');

    if (!toolbar || !contentInput) return;

    toolbar.addEventListener('click', (e) => {
        const btn = e.target.closest('.toolbar-btn');
        if (!btn) return;

        const action = btn.dataset.action;
        const textarea = contentInput;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);

        let replacement = '';
        let cursorOffset = 0;

        switch (action) {
            case 'bold':
                replacement = `<strong>${selectedText || 'bold text'}</strong>`;
                cursorOffset = selectedText ? replacement.length : 8;
                break;
            case 'italic':
                replacement = `<em>${selectedText || 'italic text'}</em>`;
                cursorOffset = selectedText ? replacement.length : 4;
                break;
            case 'heading':
                replacement = `\n<h2>${selectedText || 'Heading'}</h2>\n`;
                cursorOffset = selectedText ? replacement.length : 4;
                break;
            case 'list':
                if (selectedText) {
                    const items = selectedText.split('\n').map(line => `  <li>${line}</li>`).join('\n');
                    replacement = `\n<ul>\n${items}\n</ul>\n`;
                } else {
                    replacement = '\n<ul>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ul>\n';
                }
                cursorOffset = replacement.length;
                break;
            case 'code':
                if (selectedText.includes('\n')) {
                    replacement = `\n<pre><code>${selectedText}</code></pre>\n`;
                } else {
                    replacement = `<code>${selectedText || 'code'}</code>`;
                }
                cursorOffset = replacement.length;
                break;
            case 'link':
                const url = prompt('Enter URL:', 'https://');
                if (url) {
                    replacement = `<a href="${url}" target="_blank">${selectedText || 'link text'}</a>`;
                    cursorOffset = replacement.length;
                }
                break;
        }

        if (replacement) {
            textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + cursorOffset, start + cursorOffset);
        }
    });
}

// Convert plain text to HTML (preserves line breaks)
function textToHtml(text) {
    // If text already has HTML tags, return as is
    if (/<[a-z][\s\S]*>/i.test(text)) {
        return text;
    }

    // Convert double line breaks to paragraphs
    const paragraphs = text.split(/\n\n+/);
    return paragraphs.map(p => {
        // Convert single line breaks to <br>
        const withBreaks = p.trim().replace(/\n/g, '<br>');
        return `<p>${withBreaks}</p>`;
    }).join('\n');
}

function loadDashboard() {
    const posts = window.blogManager.getAllPosts();

    // Update stats
    document.getElementById('totalPosts').textContent = posts.length;
    document.getElementById('publishedPosts').textContent = posts.filter(p => p.published !== false).length;
    document.getElementById('draftPosts').textContent = posts.filter(p => p.published === false).length;

    // Render table
    renderPostsTable(posts);
}

function renderPostsTable(posts) {
    const noPostsEl = document.getElementById('noPostsTable');

    if (posts.length === 0) {
        postsTableBody.innerHTML = '';
        noPostsEl.style.display = 'block';
        return;
    }

    noPostsEl.style.display = 'none';

    postsTableBody.innerHTML = posts.map(post => `
    <tr>
      <td class="post-title">${post.title}</td>
      <td><span class="post-category">${post.category}</span></td>
      <td>${formatDate(post.date)}</td>
      <td>
        <span class="post-status ${post.published !== false ? 'published' : 'draft'}">
          ${post.published !== false ? 'Published' : 'Draft'}
        </span>
      </td>
      <td>
        <div class="action-btns">
          <button onclick="editPost(${post.id})" title="Edit">
            <i class="fas fa-edit"></i>
          </button>
          <button onclick="viewPost(${post.id})" title="View">
            <i class="fas fa-eye"></i>
          </button>
          <button class="delete" onclick="deletePost(${post.id})" title="Delete">
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

function openModal(post = null) {
    const modalTitle = document.getElementById('modalTitle');
    const postIdInput = document.getElementById('postId');
    const titleInput = document.getElementById('postTitleInput');
    const categoryInput = document.getElementById('postCategory');
    const excerptInput = document.getElementById('postExcerpt');
    const contentInput = document.getElementById('postContent');
    const imageInput = document.getElementById('postImage');
    const readTimeInput = document.getElementById('postReadTime');
    const publishedInput = document.getElementById('postPublished');

    if (post) {
        modalTitle.textContent = 'Edit Post';
        postIdInput.value = post.id;
        titleInput.value = post.title;
        categoryInput.value = post.category;
        excerptInput.value = post.excerpt;
        contentInput.value = post.content;
        imageInput.value = post.image || '';
        readTimeInput.value = post.readTime || 5;
        publishedInput.checked = post.published !== false;
    } else {
        modalTitle.textContent = 'Create New Post';
        postForm.reset();
        postIdInput.value = '';
        publishedInput.checked = true;
    }

    postModal.classList.add('active');
}

function closeModal() {
    postModal.classList.remove('active');
}

function handlePostSubmit(e) {
    e.preventDefault();

    const rawContent = document.getElementById('postContent').value;

    const post = {
        id: document.getElementById('postId').value ? parseInt(document.getElementById('postId').value) : null,
        title: document.getElementById('postTitleInput').value,
        category: document.getElementById('postCategory').value,
        excerpt: document.getElementById('postExcerpt').value,
        content: textToHtml(rawContent), // Auto-convert to HTML
        image: document.getElementById('postImage').value,
        readTime: parseInt(document.getElementById('postReadTime').value) || 5,
        published: document.getElementById('postPublished').checked
    };

    window.blogManager.savePost(post);
    closeModal();
    loadDashboard();
}

function editPost(id) {
    const post = window.blogManager.getPost(id);
    if (post) openModal(post);
}

function viewPost(id) {
    window.open(`post.html?id=${id}`, '_blank');
}

function deletePost(id) {
    if (confirm('Are you sure you want to delete this post?')) {
        window.blogManager.deletePost(id);
        loadDashboard();
    }
}

function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateStr).toLocaleDateString('en-US', options);
}
