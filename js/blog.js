// =============================================
// BLOG SYSTEM - Blog Management & Display
// =============================================

// Sample blog posts (will be replaced/extended by admin)
const defaultPosts = [
    {
        id: 1,
        title: "Getting Started with LangChain and RAG Systems",
        excerpt: "Learn how to build powerful Retrieval Augmented Generation systems using LangChain and vector databases for context-aware AI applications.",
        content: `<p>Retrieval Augmented Generation (RAG) is revolutionizing how we build AI applications. In this guide, I'll walk you through creating a production-ready RAG system.</p>
    
<h2>What is RAG?</h2>
<p>RAG combines the power of large language models with external knowledge retrieval, allowing AI to access and reason over your specific data.</p>

<h2>Key Components</h2>
<ul>
<li><strong>Document Loader</strong>: Ingest documents from various sources</li>
<li><strong>Text Splitter</strong>: Chunk documents for optimal retrieval</li>
<li><strong>Vector Store</strong>: Store embeddings for semantic search</li>
<li><strong>Retriever</strong>: Find relevant context for queries</li>
<li><strong>LLM Chain</strong>: Generate responses using retrieved context</li>
</ul>

<h2>Implementation</h2>
<pre><code>from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)

# Build RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)</code></pre>

<p>This foundation can be extended with re-ranking, hybrid search, and agentic workflows for even more powerful applications.</p>`,
        category: "genai",
        date: "2025-01-15",
        readTime: 8,
        image: ""
    },
    {
        id: 2,
        title: "Building High-Performance APIs with FastAPI",
        excerpt: "Discover best practices for building blazing-fast Python APIs using FastAPI, async/await, and proper architecture patterns.",
        content: `<p>FastAPI has become my go-to framework for building production APIs. Here's why and how to get the most out of it.</p>

<h2>Why FastAPI?</h2>
<ul>
<li>Automatic OpenAPI documentation</li>
<li>Built-in data validation with Pydantic</li>
<li>Async support out of the box</li>
<li>Type hints for better developer experience</li>
</ul>

<h2>Project Structure</h2>
<pre><code>app/
├── api/
│   ├── routes/
│   └── deps.py
├── core/
│   ├── config.py
│   └── security.py
├── models/
├── schemas/
└── main.py</code></pre>

<h2>Performance Tips</h2>
<blockquote>Always use async database drivers and connection pooling for maximum throughput.</blockquote>

<p>With these patterns, I've achieved 45% improvement in API response times in production systems at Weavers Web.</p>`,
        category: "backend",
        date: "2025-01-10",
        readTime: 6,
        image: ""
    },
    {
        id: 3,
        title: "Python Async Programming: A Complete Guide",
        excerpt: "Master asynchronous programming in Python with async/await, asyncio, and learn when to use it for maximum performance.",
        content: `<p>Async programming in Python unlocks incredible performance for I/O-bound operations. Let's dive deep into how it works.</p>

<h2>Understanding the Event Loop</h2>
<p>The event loop is the core of async programming. It manages and distributes the execution of different tasks.</p>

<h2>Basic Async/Await</h2>
<pre><code>import asyncio

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    results = await asyncio.gather(
        fetch_data("https://api1.com"),
        fetch_data("https://api2.com")
    )
    return results

asyncio.run(main())</code></pre>

<h2>When to Use Async</h2>
<ul>
<li>API calls and HTTP requests</li>
<li>Database operations</li>
<li>File I/O operations</li>
<li>WebSocket connections</li>
</ul>

<p>Not suitable for CPU-bound tasks - use multiprocessing instead.</p>`,
        category: "python",
        date: "2025-01-05",
        readTime: 10,
        image: ""
    }
];

// Blog Management Class
class BlogManager {
    constructor() {
        this.storageKey = 'anupam_blog_posts';
        this.init();
    }

    init() {
        // Initialize with default posts if empty
        if (!localStorage.getItem(this.storageKey)) {
            localStorage.setItem(this.storageKey, JSON.stringify(defaultPosts));
        }
    }

    getPosts() {
        const posts = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
        return posts.filter(p => p.published !== false).sort((a, b) => new Date(b.date) - new Date(a.date));
    }

    getAllPosts() {
        return JSON.parse(localStorage.getItem(this.storageKey) || '[]')
            .sort((a, b) => new Date(b.date) - new Date(a.date));
    }

    getPost(id) {
        const posts = this.getAllPosts();
        return posts.find(p => p.id === parseInt(id));
    }

    savePost(post) {
        const posts = this.getAllPosts();
        if (post.id) {
            const index = posts.findIndex(p => p.id === post.id);
            if (index !== -1) {
                posts[index] = { ...posts[index], ...post };
            }
        } else {
            post.id = Date.now();
            post.date = new Date().toISOString().split('T')[0];
            posts.push(post);
        }
        localStorage.setItem(this.storageKey, JSON.stringify(posts));
        return post;
    }

    deletePost(id) {
        let posts = this.getAllPosts();
        posts = posts.filter(p => p.id !== parseInt(id));
        localStorage.setItem(this.storageKey, JSON.stringify(posts));
    }
}

// Initialize blog manager
const blogManager = new BlogManager();

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on blog listing or post page
    if (document.getElementById('blogGrid')) {
        initBlogListing();
    } else if (document.getElementById('blogPostContent')) {
        initBlogPost();
    }

    // Mobile menu
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    toggle?.addEventListener('click', () => {
        toggle.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
});

// Blog Listing Page
function initBlogListing() {
    const blogGrid = document.getElementById('blogGrid');
    const searchInput = document.getElementById('searchInput');
    const categoryBtns = document.querySelectorAll('.category-btn');
    const noPosts = document.getElementById('noPosts');

    let currentCategory = 'all';

    function renderPosts(filter = '') {
        const posts = blogManager.getPosts();
        let filtered = posts;

        // Category filter
        if (currentCategory !== 'all') {
            filtered = filtered.filter(p => p.category === currentCategory);
        }

        // Search filter
        if (filter) {
            filtered = filtered.filter(p =>
                p.title.toLowerCase().includes(filter.toLowerCase()) ||
                p.excerpt.toLowerCase().includes(filter.toLowerCase())
            );
        }

        if (filtered.length === 0) {
            blogGrid.innerHTML = '';
            noPosts.style.display = 'block';
            return;
        }

        noPosts.style.display = 'none';
        blogGrid.innerHTML = filtered.map(post => createBlogCard(post)).join('');
    }

    function createBlogCard(post) {
        const imageStyle = post.image
            ? `background-image: url('${post.image}');`
            : '';

        return `
      <article class="blog-card">
        <div class="blog-card-image" style="${imageStyle}">
          <span class="blog-category">${post.category}</span>
        </div>
        <div class="blog-card-content">
          <h3><a href="post.html?id=${post.id}">${post.title}</a></h3>
          <p class="blog-excerpt">${post.excerpt}</p>
          <div class="blog-meta">
            <span><i class="fas fa-calendar"></i> ${formatDate(post.date)}</span>
            <span><i class="fas fa-clock"></i> ${post.readTime} min read</span>
          </div>
        </div>
      </article>
    `;
    }

    // Event listeners
    searchInput?.addEventListener('input', (e) => renderPosts(e.target.value));

    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            renderPosts(searchInput?.value || '');
        });
    });

    // Initial render
    renderPosts();
}

// Blog Post Page
function initBlogPost() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    if (!postId) {
        window.location.href = 'blog.html';
        return;
    }

    const post = blogManager.getPost(postId);

    if (!post) {
        window.location.href = 'blog.html';
        return;
    }

    document.title = `${post.title} | Anupam Dutta`;
    document.getElementById('postTitle').textContent = post.title;
    document.getElementById('postCategory').textContent = post.category;
    document.getElementById('postDate').textContent = formatDate(post.date);
    document.getElementById('postReadTime').textContent = `${post.readTime} min read`;

    // Convert plain text to HTML if needed
    const content = formatContent(post.content);
    document.getElementById('blogPostContent').innerHTML = content;
}

// Format content - convert plain text to HTML if needed
function formatContent(text) {
    if (!text) return '';

    // If text already has HTML block tags, return as is
    if (/<(p|div|h[1-6]|ul|ol|pre|blockquote)[\s>]/i.test(text)) {
        return text;
    }

    // Convert plain text to HTML
    // Split by double line breaks for paragraphs
    const paragraphs = text.split(/\n\n+/);

    if (paragraphs.length === 1 && !text.includes('\n')) {
        // Single paragraph, no line breaks
        return `<p>${text}</p>`;
    }

    return paragraphs.map(p => {
        // Convert single line breaks to <br>
        const withBreaks = p.trim().replace(/\n/g, '<br>');
        return `<p>${withBreaks}</p>`;
    }).join('\n');
}

// Helper function
function formatDate(dateStr) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateStr).toLocaleDateString('en-US', options);
}

// Export for admin
window.blogManager = blogManager;
