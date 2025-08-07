document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('image-input');
  const preview = document.getElementById('preview');
  const errorMessage = document.getElementById('error-message');
  const analyzeButton = document.getElementById('analyze-button');
  const resultsContainer = document.getElementById('results');

  // Preview selected images
  input.addEventListener('change', () => {
    preview.innerHTML = '';
    errorMessage.textContent = '';

    const files = Array.from(input.files);
    if (files.length > 4) {
      errorMessage.textContent = 'You can upload up to 4 images only.';
      return;
    }

    files.forEach(file => {
      if (!file.type.startsWith('image/')) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = document.createElement('img');
        img.src = e.target.result;
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  });

  // Send images and prompt to server and display detected objects
  analyzeButton.addEventListener('click', async () => {
    resultsContainer.innerHTML = '';
    errorMessage.textContent = '';

    const files = Array.from(input.files);
    if (files.length === 0) {
      errorMessage.textContent = 'Please select at least one image.';
      return;
    }
    if (files.length > 4) {
      errorMessage.textContent = 'You can upload up to 4 images only.';
      return;
    }

    // Prepare form data with system prompt and image files
    const promptText = document.getElementById('prompt').value.trim() ||
      'You are an assistant that identifies objects in images and provides a brief description for each one.';
    const formData = new FormData();
    formData.append('prompt', promptText);
    files.forEach(file => formData.append('images', file));

    try {
      const response = await fetch(`${window.location.origin}/upload`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();

      data.results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'result';
        // Display filename
        const title = document.createElement('h3');
        title.textContent = item.filename;
        div.appendChild(title);
        // Display description
        const pre = document.createElement('pre');
        pre.textContent = item.description;
        div.appendChild(pre);
        resultsContainer.appendChild(div);
      });
    } catch (err) {
      console.error(err);
      errorMessage.textContent = 'Error analyzing images.';
    }
  });
});
