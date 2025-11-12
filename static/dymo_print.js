// DYMO Label Printer - Client-Side Printing
// This allows printing to a locally connected DYMO printer from the browser

function printDymoLabel(kidName, eventName, eventDate, checkinTime, checkoutCode) {
    try {
        // Check if DYMO framework is loaded
        if (typeof dymo === 'undefined') {
            console.error('DYMO Label Framework not loaded');
            return false;
        }

        // Create label XML for DYMO LabelWriter (2" x 1" label)
        var labelXml = `<?xml version="1.0" encoding="utf-8"?>
<DieCutLabel Version="8.0" Units="twips">
    <PaperOrientation>Landscape</PaperOrientation>
    <Id>Address</Id>
    <IsOutlined>false</IsOutlined>
    <PaperName>30252 Address</PaperName>
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
            <HorizontalAlignment>Left</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${kidName}</String>
                    <Attributes>
                        <Font Family="Arial" Size="18" Bold="True" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="50" Width="2000" Height="350" />
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
            <HorizontalAlignment>Left</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${eventName.substring(0, 30)}</String>
                    <Attributes>
                        <Font Family="Arial" Size="10" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="380" Width="2000" Height="200" />
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
            <HorizontalAlignment>Left</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${eventDate} • ${checkinTime}</String>
                    <Attributes>
                        <Font Family="Arial" Size="10" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="560" Width="2000" Height="200" />
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
            <HorizontalAlignment>Left</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>Checkout Code:</String>
                    <Attributes>
                        <Font Family="Arial" Size="12" Bold="False" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="740" Width="2000" Height="220" />
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
            <HorizontalAlignment>Left</HorizontalAlignment>
            <VerticalAlignment>Middle</VerticalAlignment>
            <TextFitMode>ShrinkToFit</TextFitMode>
            <UseFullFontHeight>True</UseFullFontHeight>
            <Verticalized>False</Verticalized>
            <StyledText>
                <Element>
                    <String>${checkoutCode.split('').join(' ')}</String>
                    <Attributes>
                        <Font Family="Arial" Size="24" Bold="True" Italic="False" Underline="False" Strikeout="False" />
                        <ForeColor Alpha="255" Red="0" Green="0" Blue="0" />
                    </Attributes>
                </Element>
            </StyledText>
        </TextObject>
        <Bounds X="50" Y="940" Width="2000" Height="400" />
    </ObjectInfo>
</DieCutLabel>`;

        // Load the label
        var label = dymo.label.framework.openLabelXml(labelXml);
        
        // Get printers
        var printers = dymo.label.framework.getPrinters();
        if (printers.length == 0) {
            console.error('No DYMO printers found');
            alert('No DYMO printer detected. Please connect a DYMO LabelWriter printer.');
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
        return true;
        
    } catch (e) {
        console.error('Error printing label:', e);
        alert('Error printing label: ' + e.message + '\n\nMake sure DYMO Connect software is installed and running.');
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
