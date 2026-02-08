// =============================================
// PARTICLES NETWORK - Interactive Background
// Connecting dots that react to mouse movement
// =============================================

class ParticleNetwork {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.options = {
            particleCount: 80,
            particleColor: 'rgba(102, 126, 234, 0.8)',
            lineColor: 'rgba(102, 126, 234, 0.15)',
            particleRadius: 2,
            lineDistance: 150,
            speed: 0.5
        };

        this.init();
    }

    init() {
        this.resize();
        this.createParticles();
        this.setupEvents();
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        this.particles = [];
        for (let i = 0; i < this.options.particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * this.options.speed,
                vy: (Math.random() - 0.5) * this.options.speed,
                radius: Math.random() * this.options.particleRadius + 1
            });
        }
    }

    setupEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.createParticles();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseout', () => {
            this.mouse.x = null;
            this.mouse.y = null;
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update and draw particles
        this.particles.forEach((particle, i) => {
            // Move particle
            particle.x += particle.vx;
            particle.y += particle.vy;

            // Bounce off edges
            if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;

            // Mouse interaction - push particles away
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = particle.x - this.mouse.x;
                const dy = particle.y - this.mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < this.mouse.radius) {
                    const force = (this.mouse.radius - dist) / this.mouse.radius;
                    particle.x += dx * force * 0.03;
                    particle.y += dy * force * 0.03;
                }
            }

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = this.options.particleColor;
            this.ctx.fill();

            // Connect to nearby particles
            for (let j = i + 1; j < this.particles.length; j++) {
                const other = this.particles[j];
                const dx = particle.x - other.x;
                const dy = particle.y - other.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < this.options.lineDistance) {
                    const opacity = 1 - (dist / this.options.lineDistance);
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(other.x, other.y);
                    this.ctx.strokeStyle = `rgba(102, 126, 234, ${opacity * 0.2})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
            }

            // Connect to mouse
            if (this.mouse.x !== null && this.mouse.y !== null) {
                const dx = particle.x - this.mouse.x;
                const dy = particle.y - this.mouse.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < this.mouse.radius) {
                    const opacity = 1 - (dist / this.mouse.radius);
                    this.ctx.beginPath();
                    this.ctx.moveTo(particle.x, particle.y);
                    this.ctx.lineTo(this.mouse.x, this.mouse.y);
                    this.ctx.strokeStyle = `rgba(118, 75, 162, ${opacity * 0.4})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
            }
        });

        requestAnimationFrame(() => this.animate());
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    new ParticleNetwork('particles-canvas');
});
