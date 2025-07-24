document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const customFileUploadLabel = document.querySelector('.custom-file-upload'); // Get the label for the file input
    const convertDocxToPdfBtn = document.getElementById('convertDocxToPdf');
    const convertPdfToDocxBtn = document.getElementById('convertPdfToDocx');
    const statusMsg = document.getElementById('statusMsg');
    const downloadLink = document.getElementById('downloadLink');

    // Function to reset the UI to its initial state
    function resetUI() {
        if (fileInput) {
            fileInput.value = ''; // Clear selected file
            fileInput.disabled = false; // Ensure file input is enabled
        }
        if (customFileUploadLabel) customFileUploadLabel.style.pointerEvents = 'auto'; // Ensure label is clickable

        if (convertDocxToPdfBtn) convertDocxToPdfBtn.disabled = true;
        if (convertPdfToDocxBtn) convertPdfToDocxBtn.disabled = true; // Still disabled as backend doesn't support
        if (statusMsg) statusMsg.textContent = 'Choose your document and select the desired conversion type.';
        if (downloadLink) {
            downloadLink.style.display = 'none';
            downloadLink.href = '#';
            downloadLink.textContent = 'Download Converted File'; // Reset text
        }
    }

    // Function to update the UI based on the selected file
    function updateUI(file = null) {
        if (convertDocxToPdfBtn) convertDocxToPdfBtn.disabled = true;
        if (convertPdfToDocxBtn) convertPdfToDocxBtn.disabled = true; // Always disabled
        if (downloadLink) downloadLink.style.display = 'none'; // Hide download link initially or after file selection

        if (file) {
            if (statusMsg) statusMsg.textContent = `Selected: ${file.name}`;
            if (file.name.toLowerCase().endsWith('.docx')) {
                if (convertDocxToPdfBtn) convertDocxToPdfBtn.disabled = false; // Enable DOCX to PDF
            } else {
                if (statusMsg) statusMsg.textContent = 'Please select a .docx file for conversion.';
                // Keep convert button disabled if wrong file type
            }
        } else {
            // If no file selected (e.g., after reset), go back to initial state
            resetUI();
        }
    }

    // Initial UI setup on page load
    resetUI(); // Start with a clean UI

    // Event listener for when a file is selected in the input
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            updateUI(fileInput.files[0]);
        });
    } else {
        console.error("Error: fileInput element not found. Check index.html ID.");
    }

    async function handleConvert(type) {
        const file = fileInput.files[0];

        if (!file) {
            if (statusMsg) statusMsg.textContent = "Please select a file first.";
            return;
        }

        // Prevent conversion if the type is not DOCX to PDF or file is not DOCX
        if (type === 'pdfToDocx' || !file.name.toLowerCase().endsWith('.docx')) {
            if (statusMsg) statusMsg.textContent = "Only DOCX to PDF conversion is supported.";
            return;
        }

        if (statusMsg) statusMsg.textContent = "Uploading and converting... This may take a moment.";
        // Disable all interactive elements during conversion
        if (convertDocxToPdfBtn) convertDocxToPdfBtn.disabled = true;
        if (convertPdfToDocxBtn) convertPdfToDocxBtn.disabled = true;
        if (downloadLink) downloadLink.style.display = 'none';
        if (fileInput) fileInput.disabled = true; // Disable actual file input
        if (customFileUploadLabel) customFileUploadLabel.style.pointerEvents = 'none'; // Make label unclickable

        const formData = new FormData();
        formData.append("file", file);

        try {
            const backendUrl = "http://localhost:5000/convert"; 

            const response = await fetch(backendUrl, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const blob = await response.blob(); 
                const url = window.URL.createObjectURL(blob); 
                
                const originalFileName = file.name.split('.').slice(0, -1).join('.');
                const downloadFileName = `${originalFileName}.pdf`; 

                if (downloadLink) {
                    downloadLink.href = url;
                    downloadLink.download = downloadFileName;
                    downloadLink.textContent = `Download ${downloadFileName}`;
                    downloadLink.style.display = 'inline-block'; // Show the download link
                    
                    // --- Auto-trigger download ---
                    // Create a temporary anchor element and click it
                    const tempAnchor = document.createElement('a');
                    tempAnchor.href = url;
                    tempAnchor.download = downloadFileName;
                    document.body.appendChild(tempAnchor);
                    tempAnchor.click(); // Programmatically click the link
                    document.body.removeChild(tempAnchor); // Clean up temp anchor
                    // --- End auto-trigger ---
                }
                if (statusMsg) statusMsg.textContent = "Conversion successful! Your file is downloading.";

                // --- Reset UI after a slightly longer delay to ensure download starts and user sees link ---
                setTimeout(() => {
                    window.URL.revokeObjectURL(url); // Clean up the temporary URL
                    resetUI(); // Reset the UI to initial state, making file input available again
                }, 3000); // 3-second delay before resetting UI

            } else {
                // Error handling: Re-enable inputs and buttons
                const errorText = await response.text();
                try {
                    const errorData = JSON.parse(errorText);
                    if (statusMsg) statusMsg.textContent = `Conversion failed! ${errorData.error || 'Unknown error.'}`;
                    console.error("Server error (JSON):", errorData);
                } catch (e) {
                    if (statusMsg) statusMsg.textContent = `Conversion failed! ${errorText || 'Unknown error.'}`;
                    console.error("Server error (raw text):", errorText);
                }
                // Re-enable file input and custom label on error
                if (fileInput) fileInput.disabled = false;
                if (customFileUploadLabel) customFileUploadLabel.style.pointerEvents = 'auto';
                updateUI(fileInput.files[0]); // Re-evaluate button states based on current file
            }
        } catch (err) {
            if (statusMsg) statusMsg.textContent = "Conversion failed due to a network error or server issue!";
            console.error("Fetch error:", err);
            // Re-enable file input and custom label on error
            if (fileInput) fileInput.disabled = false;
            if (customFileUploadLabel) customFileUploadLabel.style.pointerEvents = 'auto';
            updateUI(fileInput.files[0]); // Re-evaluate button states
        }
    }

    // Attach click event listeners to the conversion buttons
    if (convertDocxToPdfBtn) {
        convertDocxToPdfBtn.addEventListener('click', () => handleConvert('docxToPdf'));
    }

    if (convertPdfToDocxBtn) {
        convertPdfToDocxBtn.addEventListener('click', () => handleConvert('pdfToDocx'));
    }
});
