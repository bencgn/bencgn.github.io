const navToggle = document.querySelector(".nav-toggle");
const navLinks = Array.from(document.querySelectorAll(".site-nav a"));
const languageButtons = Array.from(document.querySelectorAll(".language-toggle button"));
const contentGrid = document.querySelector("[data-content-grid]");
const contentModal = document.querySelector("[data-content-modal]");
const modalImage = document.querySelector("[data-modal-image]");
const modalCategory = document.querySelector("[data-modal-category]");
const modalTitle = document.querySelector("[data-modal-title]");
const modalMeta = document.querySelector("[data-modal-meta]");
const modalCopy = document.querySelector("[data-modal-copy]");
const modalArticle = document.querySelector("[data-modal-article]");
const modalLink = document.querySelector("[data-modal-link]");
const modalCloseButtons = Array.from(document.querySelectorAll("[data-modal-close]"));
let currentLanguage = "en";
let publicContentItems = [];
let activeModalItem = null;

const translations = {
  en: {
    "nav.home": "Home",
    "nav.public": "Public Content",
    "nav.skill": "Skill",
    "nav.contact": "Contact",
    "hero.eyebrow": "Featured Article",
    "hero.title": "Welcome, glad you're here",
    "hero.copy": "Explore public articles, products, and tools gathered here for quick reading, useful downloads, and fresh creative updates.",
    "hero.cta": "Read Feature",
    "public.title": "Public Content",
    "public.loading": "Loading public content...",
    "public.error": "Unable to load public content.",
    "cards.1.label": "Public Update",
    "cards.1.title": "Design Notes for Open Creative Work",
    "cards.2.label": "Portfolio",
    "cards.2.title": "Selected Work Shared With The Community",
    "cards.3.label": "Creative Process",
    "cards.3.title": "Methods, Drafts, and Process References",
    "cards.4.label": "Resources",
    "cards.4.title": "Public Materials Ready To Be Replaced",
    "skills.1.title": "Architecture",
    "skills.1.count": "12 Articles",
    "skills.2.title": "Interior Design",
    "skills.2.count": "18 Articles",
    "skills.3.title": "Creative Process",
    "skills.3.count": "10 Articles",
    "about.label": "BenCGN",
    "about.title": "3D Artist/Technical Art.",
    "about.copy": "Crafts 3D models, interactive assets, and technical art with an old-world sense of form, restraint, and purpose.",
    "about.cta": "Learn More",
    "footer.explore": "Explore",
    "footer.rights": "© 2026 BenCGN. All rights reserved."
  },
  vi: {
    "nav.home": "Trang chủ",
    "nav.public": "Nội dung công khai",
    "nav.skill": "Kỹ năng",
    "nav.contact": "Liên hệ",
    "hero.eyebrow": "Bài nổi bật",
    "hero.title": "Chào mừng bạn đến đây",
    "hero.copy": "Khám phá bài viết, sản phẩm và tool public tại đây nhé. Mình gom các nội dung mở để bạn xem nhanh, tải dùng khi cần và theo dõi những cập nhật sáng tạo mới.",
    "hero.cta": "Xem bài viết",
    "public.title": "Nội dung công khai",
    "public.loading": "Đang tải nội dung công khai...",
    "public.error": "Không thể tải nội dung công khai.",
    "cards.1.label": "Cập nhật",
    "cards.1.title": "Ghi chú thiết kế cho công việc sáng tạo mở",
    "cards.2.label": "Hồ sơ",
    "cards.2.title": "Các dự án chọn lọc chia sẻ cùng cộng đồng",
    "cards.3.label": "Quy trình sáng tạo",
    "cards.3.title": "Phương pháp, bản nháp và tư liệu tham khảo",
    "cards.4.label": "Tài nguyên",
    "cards.4.title": "Tài liệu công khai sẵn sàng thay thế",
    "skills.1.title": "Kiến trúc",
    "skills.1.count": "12 bài viết",
    "skills.2.title": "Thiết kế nội thất",
    "skills.2.count": "18 bài viết",
    "skills.3.title": "Quy trình sáng tạo",
    "skills.3.count": "10 bài viết",
    "about.label": "BenCGN",
    "about.title": "3D Artist/Technical Art.",
    "about.copy": "Tạo mô hình 3D, asset tương tác và technical art theo tinh thần cổ phong: chỉn chu về hình, tiết chế trong nét, hữu dụng trong từng sản phẩm.",
    "about.cta": "Tìm hiểu thêm",
    "footer.explore": "Khám phá",
    "footer.rights": "© 2026 BenCGN. Đã đăng ký bản quyền."
  }
};

navToggle?.addEventListener("click", () => {
  document.body.classList.toggle("nav-open");
});

function setActiveNav() {
  const currentHash = window.location.hash || "#";

  navLinks.forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === currentHash);
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    document.body.classList.remove("nav-open");
  });
});

window.addEventListener("hashchange", setActiveNav);
setActiveNav();

function setLanguage(lang) {
  const safeLang = translations[lang] ? lang : "en";
  currentLanguage = safeLang;

  document.documentElement.lang = safeLang === "vi" ? "vi" : "en";
  localStorage.setItem("bencgn-language", safeLang);

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.dataset.i18n;
    const value = translations[safeLang][key];

    if (value) {
      element.textContent = value;
    }
  });

  languageButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === safeLang);
  });

  if (contentGrid && !publicContentItems.length) {
    contentGrid.innerHTML = `<p class="content-state">${translations[safeLang]["public.loading"] || translations.en["public.loading"]}</p>`;
  }

  renderPublicContent();

  if (activeModalItem && contentModal && !contentModal.hidden) {
    updateContentModal(activeModalItem);
  }
}

languageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setLanguage(button.dataset.lang);
  });
});

setLanguage(localStorage.getItem("bencgn-language") || "en");

function formatContentDate(value) {
  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(currentLanguage === "vi" ? "vi-VN" : "en-US", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(date);
}

function getCategoryLabel(category) {
  const categoryMap = {
    "Kỹ Năng": {
      en: "Skill",
      vi: "Kỹ Năng"
    },
    "Sản Phẩm": {
      en: "Product",
      vi: "Sản Phẩm"
    },
    Tool: {
      en: "Tool",
      vi: "Tool"
    },
    "Sáng Tạo": {
      en: "Creative",
      vi: "Sáng Tạo"
    }
  };

  return categoryMap[category]?.[currentLanguage] || category;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    };

    return entities[character];
  });
}

function getPublicContentTitle(item) {
  return currentLanguage === "vi" && item.titleVi ? item.titleVi : item.title;
}

function getPublicContentSummary(item) {
  if (currentLanguage === "vi" && item.summaryVi) return item.summaryVi;
  return item.summary || item.title;
}

function isLinkContent(item) {
  return item.contentType === "link";
}

function inlineMarkdown(value) {
  return escapeHtml(value)
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function markdownToHtml(markdown) {
  const blocks = [];
  const lines = String(markdown || "").split(/\r?\n/);
  let paragraph = [];

  function flushParagraph() {
    if (!paragraph.length) return;
    blocks.push(`<p>${inlineMarkdown(paragraph.join(" "))}</p>`);
    paragraph = [];
  }

  lines.forEach((line) => {
    const trimmed = line.trim();

    if (!trimmed) {
      flushParagraph();
      return;
    }

    if (trimmed.startsWith("### ")) {
      flushParagraph();
      blocks.push(`<h4>${inlineMarkdown(trimmed.slice(4))}</h4>`);
      return;
    }

    if (trimmed.startsWith("## ")) {
      flushParagraph();
      blocks.push(`<h3>${inlineMarkdown(trimmed.slice(3))}</h3>`);
      return;
    }

    if (trimmed.startsWith("# ")) {
      flushParagraph();
      blocks.push(`<h3>${inlineMarkdown(trimmed.slice(2))}</h3>`);
      return;
    }

    if (trimmed.startsWith("- ")) {
      flushParagraph();
      blocks.push(`<p class="content-modal__bullet">${inlineMarkdown(trimmed.slice(2))}</p>`);
      return;
    }

    paragraph.push(trimmed);
  });

  flushParagraph();
  return blocks.join("");
}

async function loadArticleBody(item) {
  if (!modalArticle) return;

  modalArticle.innerHTML = `<p class="content-modal__loading">${currentLanguage === "vi" ? "Đang tải nội dung..." : "Loading content..."}</p>`;

  try {
    const localizedPath = currentLanguage === "en" ? "content.en.md" : "content.md";
    let response = await fetch(`publiccontent/${item.folder}/${localizedPath}?v=${Date.now()}`, {
      cache: "no-store"
    });

    if (!response.ok && localizedPath !== "content.md") {
      response = await fetch(`publiccontent/${item.folder}/content.md?v=${Date.now()}`, {
        cache: "no-store"
      });
    }

    if (!response.ok) {
      throw new Error(`Content failed: ${response.status}`);
    }

    const markdown = await response.text();
    modalArticle.innerHTML = markdownToHtml(markdown);
  } catch (error) {
    console.error(error);
    modalArticle.innerHTML = `<p class="content-modal__loading">${currentLanguage === "vi" ? "Chưa có nội dung bài viết." : "No article content yet."}</p>`;
  }
}

function updateContentModal(item) {
  const title = getPublicContentTitle(item);
  const category = getCategoryLabel(item.category);
  const date = formatContentDate(item.date);
  const href = item.linkUrl || `publiccontent/${item.folder}/`;

  modalImage.src = item.image || "";
  modalCategory.textContent = category;
  modalTitle.textContent = title;
  modalMeta.textContent = date;
  modalCopy.textContent = getPublicContentSummary(item);
  modalLink.href = href;
  modalLink.hidden = !isLinkContent(item) || !item.linkUrl;
  loadArticleBody(item);
}

async function openContentModal(item) {
  if (!contentModal) return;

  activeModalItem = item;
  updateContentModal(item);

  contentModal.hidden = false;
  document.body.classList.add("modal-open");
  contentModal.querySelector(".content-modal__close")?.focus();
}

function closeContentModal() {
  if (!contentModal) return;

  contentModal.hidden = true;
  document.body.classList.remove("modal-open");
  activeModalItem = null;
}

function renderPublicContent() {
  if (!contentGrid || !publicContentItems.length) return;

  contentGrid.innerHTML = publicContentItems
    .map((item, index) => {
      const title = getPublicContentTitle(item);
      const category = getCategoryLabel(item.category);
      const date = formatContentDate(item.date);
      const linkBadge = isLinkContent(item)
        ? `<a class="article-open" href="${escapeHtml(item.linkUrl || "#")}" data-direct-link>OPEN CONTENT</a>`
        : "";

      return `
        <article class="article-card">
          <button class="article-link" type="button" data-content-index="${index}" aria-label="${escapeHtml(title)}">
            <img src="${escapeHtml(item.image)}" alt="" />
            <div class="article-body">
              <p>${escapeHtml(category)}</p>
              <h3>${escapeHtml(title)}</h3>
              <span>${escapeHtml(date)}</span>
            </div>
          </button>
          ${linkBadge}
        </article>
      `;
    })
    .join("");
}

contentGrid?.addEventListener("click", (event) => {
  if (event.target.closest("[data-direct-link]")) return;

  const button = event.target.closest("[data-content-index]");

  if (!button) return;

  const item = publicContentItems[Number(button.dataset.contentIndex)];

  if (item) {
    openContentModal(item);
  }
});

modalCloseButtons.forEach((button) => {
  button.addEventListener("click", closeContentModal);
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && contentModal && !contentModal.hidden) {
    closeContentModal();
  }
});

async function loadPublicContent() {
  if (!contentGrid) return;

  try {
    const response = await fetch(`publiccontent/content.json?v=${Date.now()}`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Public content manifest failed: ${response.status}`);
    }

    const data = await response.json();
    publicContentItems = Array.isArray(data.items) ? data.items : [];
    renderPublicContent();
  } catch (error) {
    console.error(error);
    contentGrid.innerHTML = `<p class="content-state">${translations[currentLanguage]["public.error"] || translations.en["public.error"]}</p>`;
  }
}

loadPublicContent();

const heroSlides = Array.from(document.querySelectorAll(".hero-slide"));
const heroDots = Array.from(document.querySelectorAll(".slider-dots button"));
let activeSlide = 0;
let slideTimer;

function showSlide(index) {
  if (!heroSlides.length) return;

  activeSlide = (index + heroSlides.length) % heroSlides.length;

  heroSlides.forEach((slide, slideIndex) => {
    slide.classList.toggle("active", slideIndex === activeSlide);
  });

  heroDots.forEach((dot, dotIndex) => {
    dot.classList.toggle("active", dotIndex === activeSlide);
  });
}

function startSlideLoop() {
  clearInterval(slideTimer);
  slideTimer = setInterval(() => {
    showSlide(activeSlide + 1);
  }, 2000);
}

heroDots.forEach((dot) => {
  dot.addEventListener("click", () => {
    showSlide(Number(dot.dataset.slide || 0));
    startSlideLoop();
  });
});

showSlide(0);
startSlideLoop();
