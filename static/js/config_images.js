// Configuration Images Handler

// Base64 encoded image data for SAFe configurations
const safeConfigImages = {
    // These will be populated with the actual base64 data of the images
    'big_picture': '',
    'core_competencies': '',
    'essential': '',
    'large_solution': '',
    'portfolio': '',
    'full': ''
};

// Function to save base64 images to the server
function saveConfigurationImages() {
    // Create canvas elements and convert the provided images to base64
    const configTypes = ['big_picture', 'core_competencies', 'essential', 'large_solution', 'portfolio', 'full'];
    
    // For each configuration, listen for the image load event and save it to the server
    configTypes.forEach((configType, index) => {
        // Create a new image element
        const img = new Image();
        
        // Load the image from the src that would be displayed in the UI
        img.onload = function() {
            // Create a canvas to draw the image
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw the image on the canvas
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            // Convert to blob and save to server
            canvas.toBlob(function(blob) {
                const formData = new FormData();
                formData.append('image', blob, configType + '.jpg');
                
                // Send to the server
                fetch(`/api/upload_safe_config_image/${configType}`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        console.log(`Successfully uploaded ${configType} configuration image`);
                    } else {
                        console.error(`Failed to upload ${configType} image:`, data.message);
                    }
                })
                .catch(error => {
                    console.error(`Error uploading ${configType} image:`, error);
                });
            }, 'image/jpeg', 0.95); // High quality JPEG
        };
        
        // Set the image source based on the index (matching the 6 images provided)
        img.src = `/static/images/safe_configurations/placeholder_${index + 1}.jpg`;
        
        // Handle loading errors
        img.onerror = function() {
            console.error(`Error loading ${configType} image`);
        };
    });
}

// Function to update the UI when a configuration is selected
function updateConfigurationImage(configType) {
    // Set the image source for the selected configuration
    $('#config-image').attr('src', `/static/images/safe_configurations/${configType}.jpg`);
    $('#config-image').attr('data-config', configType);
}

// Initialize when the document is ready
$(document).ready(function() {
    // Add event listeners for configuration buttons (if not already added)
    if (!window.configListenersInitialized) {
        $('.config-btn').on('click', function() {
            const configType = $(this).data('config');
            updateConfigurationImage(configType);
        });
        window.configListenersInitialized = true;
    }
});
