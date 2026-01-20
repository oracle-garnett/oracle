# Oracle Digital Studio: The Artisan Update

This design outlines the implementation of Oracle's creative suite, allowing her to generate, edit, and display visual art on a dedicated "Canvas."

## 1. The Canvas UI (`ui/canvas_panel.py`)
A new, secondary window that Oracle can open to show her work.
*   **Live Display:** A high-quality image viewer that updates in real-time as Oracle works.
*   **Status Overlay:** A small text area at the bottom showing what she is currently "drawing" or "editing."
*   **Auto-Focus:** The window will pop up automatically when she starts a creative task.

## 2. The Artisan Toolbox (`core/artisan_agent.py`)
A new module that handles the heavy lifting of image manipulation and generation.

### Generative Tools (The Illustrator)
*   `create_image(prompt)`: Uses an AI model (OpenAI DALL-E 3 or local Stable Diffusion) to generate a new image from scratch.
*   `sketch_concept(description)`: Creates a quick, low-fidelity placeholder if the main model is unavailable.

### Editing Tools (The Photoshop)
*   `edit_image(action, parameters)`: Uses the **Pillow (PIL)** library for:
    *   `crop`, `resize`, `rotate`.
    *   `apply_filter` (Blur, Contour, Detail, Edge Enhance).
    *   `adjust_colors` (Brightness, Contrast, Sharpness).
    *   `add_text` (Watermarking or labeling).

## 3. Integration Logic
*   **TaskExecutor:** Will be updated to recognize creative requests and route them to the `ArtisanAgent`.
*   **Memory Sync:** Every "masterpiece" created will be saved in a new `gallery/` folder and indexed in her memory so she can "remember" what she drew for you.

## 4. Permission Safeguard
Just like the Web Agent, Oracle will **always ask for permission** before using paid APIs for image generation, ensuring you are always in control of the "commission."
