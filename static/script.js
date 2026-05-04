document.addEventListener('DOMContentLoaded', () => {
  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('searchInput');

  if (searchForm && searchInput) {
    searchForm.addEventListener('submit', (event) => {
      if (!searchInput.value.trim()) {
        event.preventDefault();
        searchInput.focus();
      }
    });
  }

  document.querySelectorAll('.ai-explain-button').forEach((button) => {
    button.addEventListener('click', () => explainDictionaryEntry(button));
  });
});

function appendTextElement(parent, tagName, text, className) {
  const element = document.createElement(tagName);
  element.textContent = text;

  if (className) {
    element.className = className;
  }

  parent.appendChild(element);
  return element;
}

function renderAiExplanation(container, payload) {
  const explanation = payload.explanation;
  container.innerHTML = '';

  appendTextElement(container, 'h4', 'Assistant IA');
  appendTextElement(container, 'p', explanation.summary_fr);

  const notes = document.createElement('ul');
  notes.className = 'ai-notes';
  explanation.usage_notes.forEach((note) => appendTextElement(notes, 'li', note));
  container.appendChild(notes);

  const examples = document.createElement('div');
  examples.className = 'ai-examples';
  explanation.examples.forEach((example) => {
    const exampleItem = document.createElement('p');
    appendTextElement(exampleItem, 'strong', example.fr);
    exampleItem.append(' ');
    appendTextElement(exampleItem, 'span', example.monegasque);
    examples.appendChild(exampleItem);
  });
  container.appendChild(examples);

  appendTextElement(container, 'p', explanation.memory_tip, 'ai-memory-tip');
  appendTextElement(container, 'p', explanation.practice_question, 'ai-practice-question');
}

function renderAiMessage(container, message, className) {
  container.innerHTML = '';
  appendTextElement(container, 'p', message, className);
}

function explainDictionaryEntry(button) {
  const resultItem = button.closest('.result-item');
  const container = resultItem.querySelector('.ai-explanation');

  container.hidden = false;
  button.disabled = true;
  renderAiMessage(container, 'Analyse en cours...', 'ai-loading');

  fetch('/api/ai/explain', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      word: button.dataset.word,
      definition: button.dataset.definition,
    }),
  })
    .then((response) => response.json().then((payload) => ({ response, payload })))
    .then(({ response, payload }) => {
      if (!response.ok) {
        renderAiMessage(container, payload.error || 'Assistant IA indisponible.', 'ai-error');
        return;
      }

      renderAiExplanation(container, payload);
    })
    .catch(() => {
      renderAiMessage(container, 'Assistant IA indisponible.', 'ai-error');
    })
    .finally(() => {
      button.disabled = false;
    });
}
