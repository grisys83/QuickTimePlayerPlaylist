#!/usr/bin/env python3
"""
Create templates from captured debug images
"""

import cv2
import numpy as np
from pathlib import Path
import subprocess
import os

class TemplateCreator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self.debug_dirs = list(Path(__file__).parent.glob("debug/*/"))
        
    def list_debug_images(self):
        """List all available debug images"""
        print("📁 Available debug images:")
        images = []
        
        for debug_dir in sorted(self.debug_dirs, reverse=True)[:5]:  # Last 5 sessions
            print(f"\n📂 {debug_dir.name}:")
            for img in sorted(debug_dir.glob("*.png")):
                print(f"   {img.name}")
                images.append(img)
                
        return images
    
    def open_image_for_editing(self, image_path):
        """Open image in Preview for cropping"""
        print(f"\n🖼️  Opening {image_path.name} in Preview...")
        subprocess.run(["open", "-a", "Preview", str(image_path)])
        
    def extract_region(self, image_path, x, y, width, height, output_name):
        """Extract a region from image"""
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"❌ Could not load image: {image_path}")
            return False
            
        # Extract region
        region = img[y:y+height, x:x+width]
        
        # Save
        output_path = self.template_dir / output_name
        cv2.imwrite(str(output_path), region)
        print(f"✅ Saved template: {output_path}")
        return True
    
    def interactive_template_creation(self):
        """Interactive mode to create templates"""
        print("\n🎯 Interactive Template Creation")
        print("This will help you create templates from captured images")
        
        # Find images with controls visible
        control_images = []
        menu_images = []
        
        for debug_dir in self.debug_dirs[:5]:
            # Look for images with controls
            for img in debug_dir.glob("*controls*.png"):
                control_images.append(img)
            # Look for menu images
            for img in debug_dir.glob("*menu*.png"):
                menu_images.append(img)
        
        if not control_images and not menu_images:
            print("❌ No debug images found with controls or menu")
            print("Run the automation first to generate debug images")
            return
            
        # Create AirPlay icon template
        if control_images:
            print("\n1️⃣ Creating AirPlay icon template")
            print("Found control bar images:")
            for i, img in enumerate(control_images[:3]):
                print(f"   {i+1}. {img.parent.name}/{img.name}")
                
            choice = input("\nWhich image to use? (1-3): ")
            if choice.isdigit() and 1 <= int(choice) <= len(control_images):
                selected = control_images[int(choice)-1]
                self.create_template_with_preview(selected, "airplay_icon.png", "AirPlay icon")
        
        # Create menu templates
        if menu_images:
            print("\n2️⃣ Creating menu templates")
            print("Found menu images:")
            for i, img in enumerate(menu_images[:3]):
                print(f"   {i+1}. {img.parent.name}/{img.name}")
                
            choice = input("\nWhich image to use? (1-3): ")
            if choice.isdigit() and 1 <= int(choice) <= len(menu_images):
                selected = menu_images[int(choice)-1]
                
                # Create Apple TV template
                print("\n📺 Creating Apple TV text template")
                self.create_template_with_preview(selected, "apple_tv.png", "Apple TV text (no checkbox)")
                
                # Create checkbox templates
                print("\n☑️ Creating checkbox templates")
                self.create_template_with_preview(selected, "checkbox_unchecked.png", "unchecked checkbox")
                self.create_template_with_preview(selected, "checkbox_checked.png", "checked checkbox (if visible)")
    
    def create_template_with_preview(self, source_image, output_name, description):
        """Create a template with manual region selection"""
        print(f"\n📍 Creating template for: {description}")
        
        # Load and display image
        img = cv2.imread(str(source_image))
        if img is None:
            print(f"❌ Could not load image")
            return
            
        # Create a window for selection
        window_name = f"Select {description} - Press SPACE when done, ESC to cancel"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, img)
        
        # Mouse callback for selection
        selection = {'start': None, 'end': None, 'selecting': False}
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                selection['start'] = (x, y)
                selection['selecting'] = True
            elif event == cv2.EVENT_MOUSEMOVE and selection['selecting']:
                selection['end'] = (x, y)
                # Draw rectangle
                img_copy = img.copy()
                if selection['start']:
                    cv2.rectangle(img_copy, selection['start'], (x, y), (0, 255, 0), 2)
                cv2.imshow(window_name, img_copy)
            elif event == cv2.EVENT_LBUTTONUP:
                selection['end'] = (x, y)
                selection['selecting'] = False
                # Draw final rectangle
                img_copy = img.copy()
                if selection['start'] and selection['end']:
                    cv2.rectangle(img_copy, selection['start'], selection['end'], (0, 255, 0), 2)
                cv2.imshow(window_name, img_copy)
        
        cv2.setMouseCallback(window_name, mouse_callback)
        
        print("🖱️  Click and drag to select the region")
        print("   Press SPACE to save, ESC to cancel")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("❌ Cancelled")
                cv2.destroyWindow(window_name)
                return
            elif key == 32:  # SPACE
                if selection['start'] and selection['end']:
                    # Extract region
                    x1 = min(selection['start'][0], selection['end'][0])
                    y1 = min(selection['start'][1], selection['end'][1])
                    x2 = max(selection['start'][0], selection['end'][0])
                    y2 = max(selection['start'][1], selection['end'][1])
                    
                    if x2 > x1 and y2 > y1:
                        region = img[y1:y2, x1:x2]
                        output_path = self.template_dir / output_name
                        cv2.imwrite(str(output_path), region)
                        print(f"✅ Saved: {output_path}")
                        cv2.destroyWindow(window_name)
                        return
                    else:
                        print("⚠️  Invalid selection")
    
    def auto_create_from_latest(self):
        """Automatically create templates from latest debug session"""
        print("\n🤖 Auto-creating templates from latest session")
        
        if not self.debug_dirs:
            print("❌ No debug directories found")
            return
            
        latest_dir = sorted(self.debug_dirs, reverse=True)[0]
        print(f"Using: {latest_dir}")
        
        # Copy specific images as templates if they contain the elements
        mappings = [
            ("*airplay_found*.png", "airplay_icon.png", "AirPlay icon"),
            ("*menu*.png", None, "Menu elements")  # Will extract multiple templates
        ]
        
        for pattern, output, description in mappings:
            matches = list(latest_dir.glob(pattern))
            if matches:
                source = matches[0]
                if output:
                    print(f"\n🔄 Using {source.name} for {description}")
                    print("Note: This is the full image, you should crop it manually")
                    self.open_image_for_editing(source)
                else:
                    print(f"\n📋 {source.name} contains menu - extract templates manually")
                    self.create_template_with_preview(source, "apple_tv.png", "Apple TV text")
                    self.create_template_with_preview(source, "checkbox_unchecked.png", "checkbox")


def main():
    creator = TemplateCreator()
    
    print("🎨 Template Creator from Debug Images")
    print("=" * 50)
    print("\nThis tool helps create templates from captured debug images")
    print("(Since we can't screenshot while QuickTime has focus)")
    
    print("\nOptions:")
    print("1. Interactive template creation")
    print("2. Auto-create from latest session")
    print("3. List all debug images")
    print("4. Manual instructions")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == "1":
        creator.interactive_template_creation()
    elif choice == "2":
        creator.auto_create_from_latest()
    elif choice == "3":
        creator.list_debug_images()
    elif choice == "4":
        print("\n📝 Manual Instructions:")
        print("1. Run 'python3 universal_airplay_automation.py' first")
        print("2. This will create debug images in the debug/ folder")
        print("3. Find images like:")
        print("   - *_with_controls.png - Contains AirPlay icon")
        print("   - *_airplay_menu.png - Contains checkbox and Apple TV text")
        print("4. Use any image editor to crop:")
        print("   - Just the AirPlay icon → save as templates/airplay_icon.png")
        print("   - Just the checkbox → save as templates/checkbox_unchecked.png")
        print("   - Just 'Apple TV' text → save as templates/apple_tv.png")
        
        # Show where to find images
        if creator.debug_dirs:
            latest = sorted(creator.debug_dirs, reverse=True)[0]
            print(f"\n📁 Latest debug folder: {latest}")
            subprocess.run(["open", str(latest)])


if __name__ == "__main__":
    main()