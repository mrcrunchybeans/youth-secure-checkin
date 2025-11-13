// DYMO Label Printer - Client-Side Printing
// This allows printing to a locally connected DYMO printer from the browser

function printDymoLabel(kidName, eventName, eventDate, checkinTime, checkoutCode) {
    try {
        // Check if DYMO framework is loaded
        if (typeof dymo === 'undefined') {
            console.error('DYMO Label Framework not loaded');
            showPrintError('DYMO Label Framework not available.<br><br>' +
                         '<strong>To enable label printing:</strong><br>' +
                         '1. Download and install <a href="https://www.dymo.com/support" target="_blank" class="text-white"><u>DYMO Connect</u></a><br>' +
                         '2. Connect your DYMO LabelWriter printer<br>' +
                         '3. Ensure DYMO Connect is running<br>' +
                         '4. Refresh this page');
            return false;
        }

        // Create label XML for DYMO LabelWriter (1" x 2.125" label - 30336)
        var labelXml = `<?xml version="1.0" encoding="utf-8"?>
<DieCutLabel Version="8.0" Units="twips">
    <PaperOrientation>Portrait</PaperOrientation>
    <Id>Small</Id>
    <IsOutlined>false</IsOutlined>
    <PaperName>30336 1 in x 2-1/8 in</PaperName>
    <DrawCommands/>
    <ObjectInfo>
        <TextObject>
            <Name>KidName</Name>
            <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
            <BackColor Alpha="0" Red="255" Green="255" Blue="255" />
            <LinkedObjectName/>
            <Rotation>Rotation0</Rotation>
            <IsMirrored>False</IsMirrored>
            <IsVariable>True</IsVariable>
            <HorizontalAlignment>Center</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${kidName}</String>
                    <Attributes>
                        <Font Family="Arial" Size="12" Bold="True" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="50" Width="1340" Height="320" />
    </ObjectInfo>
    <ObjectInfo>
        <TextObject>
            <Name>EventInfo</Name>
            <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
            <BackColor Alpha="0" Red="255" Green="255" Blue="255" />
            <LinkedObjectName/>
            <Rotation>Rotation0</Rotation>
            <IsMirrored>False</IsMirrored>
            <IsVariable>True</IsVariable>
            <HorizontalAlignment>Center</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${eventName.substring(0, 20)}</String>
                    <Attributes>
                        <Font Family="Arial" Size="8" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="360" Width="1340" Height="180" />
    </ObjectInfo>
    <ObjectInfo>
        <TextObject>
            <Name>DateTime</Name>
            <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
            <BackColor Alpha="0" Red="255" Green="255" Blue="255" />
            <LinkedObjectName/>
            <Rotation>Rotation0</Rotation>
            <IsMirrored>False</IsMirrored>
            <IsVariable>True</IsVariable>
            <HorizontalAlignment>Center</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${eventDate} ${checkinTime}</String>
                    <Attributes>
                        <Font Family="Arial" Size="7" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="530" Width="1340" Height="160" />
    </ObjectInfo>
    <ObjectInfo>
        <TextObject>
            <Name>CodeLabel</Name>
            <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
            <BackColor Alpha="0" Red="255" Green="255" Blue="255" />
            <LinkedObjectName/>
            <Rotation>Rotation0</Rotation>
            <IsMirrored>False</IsMirrored>
            <IsVariable>True</IsVariable>
            <HorizontalAlignment>Center</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>Code:</String>
                    <Attributes>
                        <Font Family="Arial" Size="8" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="680" Width="1340" Height="160" />
    </ObjectInfo>
    <ObjectInfo>
        <TextObject>
            <Name>CheckoutCode</Name>
            <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
            <BackColor Alpha="0" Red="255" Green="255" Blue="255" />
            <LinkedObjectName/>
            <Rotation>Rotation0</Rotation>
            <IsMirrored>False</IsMirrored>
            <IsVariable>True</IsVariable>
            <HorizontalAlignment>Center</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${checkoutCode}</String>
                    <Attributes>
                        <Font Family="Courier New" Size="16" Bold="True" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="830" Width="1340" Height="400" />
    </ObjectInfo>
</DieCutLabel>`;

        // Load the label
        var label = dymo.label.framework.openLabelXml(labelXml);
        
        // Get printers
        var printers = dymo.label.framework.getPrinters();
        if (printers.length == 0) {
            console.error('No DYMO printers found');
            showPrintError('No DYMO printer detected.<br><br>' +
                         '<strong>Troubleshooting:</strong><br>' +
                         '1. Connect DYMO LabelWriter via USB<br>' +
                         '2. Make sure DYMO Connect is running<br>' +
                         '3. Check printer shows up in DYMO Connect<br>' +
                         '4. Try restarting DYMO Connect');
            return false;
        }
        
        // Find a DYMO LabelWriter printer
        var printerName = "";
        for (var i = 0; i < printers.length; i++) {
            var printer = printers[i];
            if (printer.printerType == "LabelWriterPrinter") {
                printerName = printer.name;
                break;
            }
        }
        
        if (!printerName) {
            printerName = printers[0].name; // Use first printer if no LabelWriter found
        }
        
        console.log('Printing to: ' + printerName);
        
        // Print the label
        label.print(printerName);
        
        console.log('Label sent to printer successfully');
        showPrintSuccess('Label printed successfully to ' + printerName);
        return true;
        
    } catch (e) {
        console.error('Error printing label:', e);
        showPrintError('Error printing label: ' + e.message + '<br><br>' +
                     'Make sure DYMO Connect is installed and running.<br>' +
                     'Download from: <a href="https://www.dymo.com/support" target="_blank" class="text-white"><u>dymo.com/support</u></a>');
        return false;
    }
}

// Check if DYMO framework is ready
function checkDymoStatus() {
    try {
        if (typeof dymo === 'undefined') {
            return {ready: false, message: 'DYMO framework not loaded'};
        }
        
        var printers = dymo.label.framework.getPrinters();
        if (printers.length == 0) {
            return {ready: false, message: 'No DYMO printers detected'};
        }
        
        return {ready: true, message: 'DYMO printer ready', printers: printers};
    } catch (e) {
        return {ready: false, message: 'DYMO error: ' + e.message};
    }
}

// Show print error notification
function showPrintError(message) {
    // Create toast notification
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>⚠️ Print Failed</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast, {delay: 10000}); // Show for 10 seconds
    bsToast.show();
    
    // Remove from DOM after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Show print success notification
function showPrintSuccess(message) {
    // Create toast notification
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    toast.setAttribute('aria-atomic', 'true');
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>✅ Label Printed</strong><br>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    var bsToast = new bootstrap.Toast(toast, {delay: 3000}); // Show for 3 seconds
    bsToast.show();
    
    // Remove from DOM after hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
