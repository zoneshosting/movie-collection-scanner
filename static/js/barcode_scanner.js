/**
 * Movie Collection Barcode Scanner
 * 
 * This module provides barcode scanning functionality for the movie collection app.
 * It supports webcam scanning on desktop and camera scanning on mobile devices.
 */

class MovieBarcodeScanner {
    constructor(htmlElementId) {
        this.htmlElementId = htmlElementId;
        this.html5QrCode = null;
        this.lastResult = null;
        this.isScanning = false;
    }

    /**
     * Initialize the scanner
     * @param {Function} onScanSuccess - Callback function when a barcode is successfully scanned
     * @param {Function} onScanFailure - Optional callback function when scanning fails
     */
    init(onScanSuccess, onScanFailure = null) {
        // Create instance of the scanner
        this.html5QrCode = new Html5Qrcode(this.htmlElementId);
        
        // Store callbacks
        this.onScanSuccess = (decodedText, decodedResult) => {
            // Prevent duplicate scans of the same barcode
            if (this.lastResult !== decodedText) {
                this.lastResult = decodedText;
                console.log(`Barcode scanned: ${decodedText}`, decodedResult);
                
                // Display scanning animation or feedback
                this.showScanFeedback();
                
                // Call the user-provided success callback
                onScanSuccess(decodedText, decodedResult);
            }
        };
        
        this.onScanFailure = (errorMessage) => {
            // Only call the user's failure callback if it was provided
            if (onScanFailure) {
                onScanFailure(errorMessage);
            }
        };
    }

    /**
     * Start scanning with the camera
     * @param {boolean} useFrontCamera - Whether to use front camera on mobile (default: false)
     */
    startScanner(useFrontCamera = false) {
        if (this.isScanning) {
            return;
        }

        // Get all cameras
        Html5Qrcode.getCameras()
            .then(cameras => {
                if (cameras && cameras.length) {
                    const facingMode = useFrontCamera ? "user" : "environment";
                    
                    // Configure scanner options
                    const config = {
                        fps: 10,
                        qrbox: { width: 250, height: 150 }, // Adjusted for 1D barcodes which are wider than tall
                        formatsToSupport: [
                            Html5QrcodeSupportedFormats.EAN_13,
                            Html5QrcodeSupportedFormats.EAN_8,
                            Html5QrcodeSupportedFormats.UPC_A,
                            Html5QrcodeSupportedFormats.UPC_E,
                            Html5QrcodeSupportedFormats.CODE_128
                        ]
                    };

                    this.html5QrCode.start(
                        { facingMode: facingMode },
                        config,
                        this.onScanSuccess,
                        this.onScanFailure
                    )
                    .then(() => {
                        this.isScanning = true;
                        this.showScannerUI(true);
                    })
                    .catch(err => {
                        console.error("Error starting scanner:", err);
                        alert("Could not start camera scanner. Please check camera permissions.");
                    });
                } else {
                    alert("No cameras found on your device!");
                }
            })
            .catch(err => {
                console.error("Error getting cameras:", err);
                alert("Could not access camera. Please check permissions.");
            });
    }

    /**
     * Stop the scanner
     */
    stopScanner() {
        if (this.isScanning) {
            this.html5QrCode.stop()
                .then(() => {
                    this.isScanning = false;
                    this.showScannerUI(false);
                })
                .catch(err => {
                    console.error("Error stopping scanner:", err);
                });
        }
    }

    /**
     * Toggle front/back camera on mobile devices
     */
    toggleCamera() {
        const currentState = this.isScanning;
        if (currentState) {
            this.stopScanner();
            // Use setTimeout to ensure camera is fully stopped before restarting
            setTimeout(() => {
                this.startScanner(!this.usingFrontCamera);
                this.usingFrontCamera = !this.usingFrontCamera;
            }, 300);
        }
    }

    /**
     * Toggle flashlight/torch if supported
     */
    toggleFlash() {
        if (this.isScanning) {
            this.html5QrCode.getRunningTrackCapabilities()
                .then(capabilities => {
                    if (capabilities && capabilities.torch) {
                        // Get current torch status
                        return this.html5QrCode.getRunningTrackSettings()
                            .then(settings => {
                                const currentTorch = settings.torch || false;
                                return this.html5QrCode.applyVideoConstraints({
                                    advanced: [{ torch: !currentTorch }]
                                });
                            });
                    } else {
                        alert("Torch/flashlight not supported on this device or browser");
                    }
                })
                .catch(err => {
                    console.error("Error toggling flash:", err);
                });
        }
    }

    /**
     * Show visual feedback when a barcode is scanned
     */
    showScanFeedback() {
        const scanRegion = document.getElementById(this.htmlElementId);
        if (scanRegion) {
            // Add a temporary class for animation
            scanRegion.classList.add('barcode-scanned');
            
            // Remove the class after animation completes
            setTimeout(() => {
                scanRegion.classList.remove('barcode-scanned');
            }, 500);
        }
    }

    /**
     * Show/hide scanner UI elements
     * @param {boolean} show - Whether to show or hide the scanner UI
     */
    showScannerUI(show) {
        const scanControls = document.getElementById('scanner-controls');
        if (scanControls) {
            scanControls.style.display = show ? 'flex' : 'none';
        }
    }

    /**
     * Clean up resources when the scanner is no longer needed
     */
    dispose() {
        if (this.isScanning) {
            this.stopScanner();
        }
    }
}

// Export the scanner class
window.MovieBarcodeScanner = MovieBarcodeScanner;
