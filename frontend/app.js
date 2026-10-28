/**
 * app.js
 *
 * Sends the user's Emotion and Weight to `POST /ask` and renders the
 * Re-cooked Recipe with its Original Recipe citation (see GLOSSARY.md).
 */

/**
 * @typedef {Object} SourceChunk
 * @property {string} label
 * @property {string} [chapter]
 * @property {string} [book_title]
 * @property {string} [file_name]
 * @property {string} [source_path]
 * @property {string} text
 */

/**
 * @typedef {Object} AskResponse
 * @property {string} answer
 * @property {string[]} citations
 * @property {SourceChunk[]} sources
 */

const form = document.getElementById("poem-form");
const emotionInput = document.getElementById("emotion");
const weightInput = document.getElementById("weight");
const weightValue = document.getElementById("weight-value");
const submitBtn = document.getElementById("submit-btn");
const errorMessage = document.getElementById("error-message");
const outputSection = document.getElementById("output-section");
const output = document.getElementById("output");
const explanationContent = document.getElementById("explanation-content");

/**
 * @param {{ question: string, additional_context?: string, temperature?: number }} payload
 * @returns {Promise<AskResponse>}
 */
async function askQuestion(payload) {
  const response = await fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Backend responded with an error");
  }

  return response.json();
}

/** Create an element with an optional class and text content. */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function setLoading(loading) {
  submitBtn.disabled = loading;
  submitBtn.replaceChildren();
  if (loading) {
    const loader = el("span", "btn-loader");
    loader.append(el("span", "spinner"), " Đang tạo công thức...");
    submitBtn.append(loader);
  } else {
    submitBtn.append(el("span", "btn-text", "Tạo công thức"));
  }
}

/** Render `**bold**` segments of the answer as <strong>, the rest as plain text. */
function renderAnswer(answer) {
  output.replaceChildren(
    ...answer
      .split(/(\*\*.*?\*\*)/g)
      .map((part) =>
        part.startsWith("**") && part.endsWith("**")
          ? el("strong", "", part.slice(2, -2))
          : el("span", "", part)
      )
  );
}

/** @param {SourceChunk[]} sources */
function renderSources(sources) {
  if (!sources || sources.length === 0) {
    explanationContent.replaceChildren(
      el("p", "text-center", "Không có thông tin tham khảo.")
    );
    return;
  }

  explanationContent.replaceChildren(
    ...sources.map((source) => {
      const item = el("div", "keyword-item");

      const bookTitle = el("div", "keyword-detail");
      bookTitle.append(el("strong", "", "Nguồn:"), ` ${source.book_title ?? ""}`);

      const chapter = el("div", "keyword-detail");
      chapter.append(el("strong", "", "Số báo:"), ` ${source.chapter ?? ""}`);

      item.append(
        el("h4", "", source.label),
        bookTitle,
        chapter,
        el("div", "keyword-citation", source.text)
      );
      return item;
    })
  );
}

weightInput.addEventListener("input", () => {
  weightValue.textContent = `${weightInput.value} kg`;
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const emotion = emotionInput.value;
  if (!emotion.trim()) return;

  setLoading(true);
  errorMessage.hidden = true;
  outputSection.hidden = true;

  try {
    const res = await askQuestion({
      question: emotion,
      additional_context: `${weightInput.value} kg`,
    });
    renderAnswer(res.answer);
    renderSources(res.sources);
    outputSection.hidden = false;
  } catch (err) {
    console.error(err);
    errorMessage.textContent = "Có lỗi xảy ra. Vui lòng thử lại.";
    errorMessage.hidden = false;
  } finally {
    setLoading(false);
  }
});

document.getElementById("print-btn").addEventListener("click", () => {
  window.print();
});
