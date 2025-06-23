"""
Main GUI Window for Secure Secret Sharing Tool

Provides a user-friendly interface for splitting secrets into shares
and reconstructing secrets from shares.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Optional
import threading
import time

# Safe clipboard handling (pyperclip alternative)
def safe_copy_to_clipboard(text: str) -> bool:
    """Safely copy text to clipboard, return True if successful."""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        # Fallback to tkinter clipboard
        try:
            root = tk._default_root
            if root:
                root.clipboard_clear()
                root.clipboard_append(text)
                return True
        except Exception:
            pass
    except Exception:
        pass
    return False

from ..crypto.shamir import ShamirSecretSharing
from ..crypto.security import SecurityValidator, SecurityError


class SecretSharingGUI:
    """Main GUI application for secret sharing."""
    
    def __init__(self):
        """Initialize the GUI application."""
        # Make the application DPI-aware for multi-monitor setups
        self._make_dpi_aware()
        
        self.root = tk.Tk()
          # Configure for high DPI and multi-monitor support
        self._configure_dpi_scaling()
        
        self.root.title("🔐 CryptoVault - Secure Secret Sharing Suite")
        self.root.geometry("1200x900")  # Larger default for better DPI support
        self.root.resizable(True, True)
        
        # Set window icon (using emoji as fallback)
        try:
            # Try to set a proper icon if available
            self.root.iconbitmap(default="icon.ico")
        except:
            # Fallback to emoji in title
            pass
        
        # Modern dark theme colors
        self.colors = {
            'bg_primary': '#1a1a1a',      # Very dark background
            'bg_secondary': '#2d2d2d',    # Card/panel background  
            'bg_accent': '#3d3d3d',       # Input backgrounds
            'fg_primary': '#ffffff',      # Primary text (white)
            'fg_secondary': '#b3b3b3',    # Secondary text (light gray)
            'fg_accent': '#00d4aa',       # Accent color (cyan-green)
            'success': '#10b981',         # Success green
            'warning': '#f59e0b',         # Warning amber
            'error': '#ef4444',           # Error red
            'button_bg': '#4f46e5',       # Button background (indigo)
            'button_hover': '#6366f1'     # Button hover (lighter indigo)
        }
        
        # Initialize crypto components
        self.shamir = ShamirSecretSharing()
        self.security = SecurityValidator()
        
        # Sensitive data storage (for clearing)
        self.sensitive_widgets = []
        
        # Configure style
        self._configure_modern_style()
        
        # Create GUI components
        self._create_widgets()
          # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _make_dpi_aware(self):
        """Make the application DPI-aware for multi-monitor setups."""
        try:
            import ctypes
            import ctypes.wintypes
            
            # Tell Windows this app is DPI aware
            # This prevents Windows from scaling our app and causing display issues
            try:
                # Try the newer SetProcessDpiAwarenessContext first (Windows 10 1607+)
                # Use DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 for best multi-monitor support
                ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
            except (AttributeError, OSError):
                try:
                    # Fallback to SetProcessDpiAwarenessContext with V1
                    ctypes.windll.user32.SetProcessDpiAwarenessContext(-3)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE
                except (AttributeError, OSError):
                    try:
                        # Fallback to SetProcessDpiAwareness (Windows 8.1+)
                        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
                    except (AttributeError, OSError):
                        try:
                            # Final fallback to SetProcessDPIAware (Windows Vista+)
                            ctypes.windll.user32.SetProcessDPIAware()
                        except (AttributeError, OSError):
                            # If all else fails, just continue without DPI awareness
                            pass
        except Exception:            # If any error occurs, continue without DPI awareness
            # This ensures the app still works on systems where these APIs aren't available
            pass

    def _configure_dpi_scaling(self):
        """Configure DPI scaling and multi-monitor support."""
        try:
            # Force tkinter to use proper system scaling - this is critical
            self.root.tk.call('tk', 'scaling', '-displayof', '.', 1.0)
            
            # Set minimum and default window size to prevent GUI elements from disappearing
            # This is crucial for multi-monitor setups
            self.root.minsize(1000, 700)  # Increased minimum size
            self.root.geometry("1200x900")  # Larger default size
            
            # Force window to center on screen initially
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{pos_x}+{pos_y}')
            
            # Enable automatic scaling for text and widgets
            # This helps maintain readability across different DPI settings
            self.root.option_add('*TkDefaultFont', 'system')
            self.root.option_add('*Dialog.msg.font', 'system')
            
            # Add comprehensive DPI change monitoring
            self.root.bind('<Configure>', self._on_window_configure)
            self.root.bind('<Map>', self._on_window_map)
            self.root.bind('<Visibility>', self._on_visibility_change)
            
            # Force initial layout update
            self.root.after_idle(self._force_layout_refresh)
            
        except Exception as e:            # If configuration fails, use safe defaults
            try:
                self.root.minsize(1000, 700)
                self.root.geometry("1200x900")
            except:
                pass

    def _on_window_configure(self, event):
        """Handle window configuration changes (including monitor moves)."""
        # Only handle configure events for the main window
        if event.widget == self.root:
            try:
                # Force a refresh of the window layout
                # This helps fix issues when moving between monitors with different DPI
                self.root.update_idletasks()
                
                # Ensure minimum size is maintained - updated for larger minimum
                current_width = self.root.winfo_width()
                current_height = self.root.winfo_height()
                
                if current_width < 1000 or current_height < 700:
                    self.root.geometry("1000x700")
                
                # Force refresh of all sensitive input widgets
                # This is crucial for fixing disappearing input boxes on monitor changes
                self._refresh_widget_visibility()
                    
            except Exception:
                # If any error occurs during reconfiguration, ignore it
                pass

    def _on_window_map(self, event):
        """Handle window mapping events (when window becomes visible)."""
        if event.widget == self.root:
            try:
                # Force layout refresh when window is mapped/shown
                self.root.after_idle(self._force_layout_refresh)
            except Exception:
                pass

    def _on_visibility_change(self, event):
        """Handle visibility change events."""
        if event.widget == self.root:
            try:
                # Force refresh when visibility changes (e.g., moving between monitors)
                self.root.after_idle(self._force_layout_refresh)
            except Exception:
                pass

    def _force_layout_refresh(self):
        """Force a complete layout refresh - critical for DPI changes."""
        try:
            # Update all widgets and force geometry recalculation
            self.root.update_idletasks()
            
            # Refresh all sensitive widgets
            self._refresh_widget_visibility()
            
            # Force a complete redraw
            self.root.update()
            
        except Exception:
            # If refresh fails, continue silently
            pass

    def _refresh_widget_visibility(self):
        """Force refresh of widget visibility after monitor/DPI changes."""
        try:
            # Update all text widgets to ensure they remain visible
            for widget in self.sensitive_widgets:
                if hasattr(widget, 'update_idletasks'):
                    widget.update_idletasks()
                    
            # Also refresh key GUI components that tend to disappear
            if hasattr(self, 'secret_input_text'):
                self.secret_input_text.update_idletasks()
            if hasattr(self, 'shares_text'):
                self.shares_text.update_idletasks()
            if hasattr(self, 'reconstructed_secret_text'):
                self.reconstructed_secret_text.update_idletasks()
            if hasattr(self, 'shares_input_text'):
                self.shares_input_text.update_idletasks()
                
            # Force geometry update for the entire window
            self.root.update()
            
        except Exception:
            # If refresh fails, continue silently
            pass
    
    def _configure_modern_style(self):
        """Configure modern dark theme styling."""
        style = ttk.Style()
        
        # Set the main background
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Use a modern theme as base
        style.theme_use('clam')
        
        # Configure modern styles with our color palette
        style.configure('Modern.TLabel', 
                       font=('Segoe UI', 11), 
                       foreground=self.colors['fg_primary'], 
                       background=self.colors['bg_primary'])
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 20, 'bold'), 
                       foreground=self.colors['fg_accent'], 
                       background=self.colors['bg_primary'])
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 14, 'bold'), 
                       foreground=self.colors['fg_accent'], 
                       background=self.colors['bg_primary'])
        
        style.configure('Info.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=self.colors['fg_secondary'], 
                       background=self.colors['bg_primary'])
        
        style.configure('Success.TLabel', 
                       font=('Segoe UI', 10), 
                       foreground=self.colors['success'], 
                       background=self.colors['bg_primary'])
        
        style.configure('Warning.TLabel', 
                       font=('Segoe UI', 10, 'bold'), 
                       foreground=self.colors['warning'], 
                       background=self.colors['bg_primary'])
        
        # Configure notebook (tabs)
        style.configure('TNotebook', 
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg_secondary'],
                       padding=[15, 10],
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_accent'])],
                 foreground=[('selected', self.colors['fg_primary'])])
        
        # Configure frames
        style.configure('Card.TFrame', 
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Main.TFrame', 
                       background=self.colors['bg_primary'])
        
        # Configure buttons
        style.configure('Action.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background=self.colors['button_bg'],
                       padding=[16, 10],
                       relief='flat')
        
        style.map('Action.TButton',
                 background=[('active', self.colors['button_hover'])])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['fg_primary'],
                       background=self.colors['bg_accent'],
                       padding=[12, 8],
                       relief='flat')
        
        style.configure('Clear.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground='white',
                       background=self.colors['error'],
                       padding=[12, 8],
                       relief='flat')
        
        # Configure entry/spinbox
        style.configure('Modern.TSpinbox',
                       fieldbackground=self.colors['bg_accent'],
                       background=self.colors['bg_accent'],                       foreground=self.colors['fg_primary'],
                       borderwidth=1,
                       relief='solid')
    
    def _create_widgets(self):
        """Create and layout modern GUI widgets with optimized spacing."""
        # Main container with reduced padding for more space
        main_frame = ttk.Frame(self.root, padding="15", style='Main.TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Compact header section
        header_frame = ttk.Frame(main_frame, style='Main.TFrame')
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # Compact title - smaller font and reduced spacing
        title_label = ttk.Label(header_frame, 
                               text="🔐 CryptoVault - Secure Secret Sharing", 
                               font=('Segoe UI', 16, 'bold'),
                               foreground=self.colors['fg_accent'],
                               background=self.colors['bg_primary'])
        title_label.grid(row=0, column=0, sticky="w")
        
        # Compact security warning - smaller and inline
        warning_frame = ttk.Frame(header_frame, style='Main.TFrame')
        warning_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))        
        warning_label = ttk.Label(warning_frame, 
                                text="⚠️ Air-gapped devices only", 
                                font=('Segoe UI', 12),
                                foreground=self.colors['warning'],
                                background=self.colors['bg_primary'])
        warning_label.grid(row=0, column=0, sticky="w")
        
        # Create notebook for tabs with minimal spacing
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 8))
        main_frame.rowconfigure(1, weight=1)
        
        # Create tabs
        self._create_split_tab()
        self._create_reconstruct_tab()
        
        # Compact status and clear button row
        bottom_frame = ttk.Frame(main_frame, style='Main.TFrame')
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Status bar - more compact
        self.status_var = tk.StringVar(value="✅ Ready")
        status_label = ttk.Label(bottom_frame, textvariable=self.status_var, 
                               font=('Segoe UI', 9),
                               foreground=self.colors['success'],
                               background=self.colors['bg_primary'])
        status_label.grid(row=0, column=0, sticky="w")
          # Clear all button - more compact
        clear_button = ttk.Button(bottom_frame, text="🧹 Clear All",                                 command=self._clear_all_data, 
                                 style='Clear.TButton')
        clear_button.grid(row=0, column=1, sticky="e")
    
    def _create_split_tab(self):
        """Create the secret splitting tab with optimized compact layout."""
        split_frame = ttk.Frame(self.notebook, padding="12", style='Main.TFrame')
        self.notebook.add(split_frame, text="🔀 Split Secret")
        
        # Compact header
        header_label = ttk.Label(split_frame, text="🔀 Split Secret into Shares", 
                               font=('Segoe UI', 12, 'bold'),
                               foreground=self.colors['fg_accent'],
                               background=self.colors['bg_primary'])
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        # Left side - Input Section with reduced padding
        input_frame = ttk.Frame(split_frame, style='Card.TFrame', padding="15")
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        
        # Input section header - more compact
        input_header = ttk.Label(input_frame, text="📝 Input", 
                               font=('Segoe UI', 11, 'bold'),
                               foreground=self.colors['fg_accent'],
                               background=self.colors['bg_secondary'])
        input_header.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Secret input with compact label
        secret_label = ttk.Label(input_frame, text="💎 Enter Secret:", 
                               font=('Segoe UI', 10),
                               foreground=self.colors['fg_primary'],
                               background=self.colors['bg_secondary'])
        secret_label.grid(row=1, column=0, sticky="wn", pady=(0, 5))
          # Create a modern text widget with custom styling
        self.secret_input_text = scrolledtext.ScrolledText(
            input_frame, height=8, width=110, wrap=tk.WORD,
            font=('Consolas', 15),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_accent'],
            selectbackground=self.colors['button_bg'],
            relief='flat',
            borderwidth=2
        )
        self.secret_input_text.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.sensitive_widgets.append(self.secret_input_text)
          # Parameters section - more compact
        params_label = ttk.Label(input_frame, text="⚙️ Config:", 
                               font=('Segoe UI', 12),
                               foreground=self.colors['fg_primary'],
                               background=self.colors['bg_secondary'])
        params_label.grid(row=3, column=0, sticky="w", pady=(8, 4))
        
        # Parameters in compact layout
        params_subframe = ttk.Frame(input_frame, style='Main.TFrame')
        params_subframe.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        
        # Total shares - more compact
        ttk.Label(params_subframe, text="Total:", 
                 font=('Segoe UI', 12),
                 foreground=self.colors['fg_primary'],
                 background=self.colors['bg_secondary']).grid(row=0, column=0, sticky="w", pady=2)
        self.total_shares_var = tk.StringVar(value="5")
        total_shares_spinbox = ttk.Spinbox(
            params_subframe, from_=2, to=20, textvariable=self.total_shares_var, 
            width=6, style='Modern.TSpinbox'
        )
        total_shares_spinbox.grid(row=0, column=1, sticky="w", padx=(8, 0), pady=2)
        
        # Threshold - more compact
        ttk.Label(params_subframe, text="Threshold:", 
                 font=('Segoe UI', 12),
                 foreground=self.colors['fg_primary'],
                 background=self.colors['bg_secondary']).grid(row=0, column=2, sticky="w", padx=(15, 0), pady=2)
        self.threshold_var = tk.StringVar(value="3")
        threshold_spinbox = ttk.Spinbox(
            params_subframe, from_=2, to=20, textvariable=self.threshold_var, 
            width=6, style='Modern.TSpinbox'
        )
        threshold_spinbox.grid(row=0, column=3, sticky="w", padx=(8, 0), pady=2)
        
        # Compact info label
        info_text = ("💡 Total=shares to create, Threshold=min to reconstruct\n� Up to 50K chars, each share ≥250 chars")
        info_label = ttk.Label(input_frame, text=info_text, 
                             font=('Segoe UI', 10),
                             foreground=self.colors['fg_secondary'],
                             background=self.colors['bg_secondary'])
        info_label.grid(row=5, column=0, sticky="w", pady=(4, 8))
        
        # Split button
        split_button = ttk.Button(input_frame, text="🔀 Split Secret", 
                                 command=self._split_secret, style='Action.TButton')
        split_button.grid(row=6, column=0, pady=(10, 0), sticky="ew")
        
        # Right side - Output Section
        output_frame = ttk.Frame(split_frame, style='Card.TFrame', padding="20")
        output_frame.grid(row=1, column=1, sticky="nsew", padx=(15, 0), pady=(0, 20))
        
        # Output section header
        output_header = ttk.Label(output_frame, text="📋 Generated Shares", style='Header.TLabel')
        output_header.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Status/instruction label
        self.shares_status = ttk.Label(output_frame, 
                                      text="✨ Your shares will appear here after splitting", 
                                      style='Info.TLabel')
        self.shares_status.grid(row=1, column=0, sticky="w", pady=(0, 8))
          # Shares display
        self.shares_text = scrolledtext.ScrolledText(
            output_frame, height=14, width=55, wrap=tk.WORD,
            font=('Consolas', 15),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_accent'],
            selectbackground=self.colors['button_bg'],
            relief='flat',
            borderwidth=2
        )
        self.shares_text.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        self.sensitive_widgets.append(self.shares_text)
        
        # Add placeholder text
        self.shares_text.insert(1.0, "🔄 Waiting for secret to split...\n\n" )
                               
                               
        
        # Copy shares button
        copy_shares_button = ttk.Button(output_frame, text="📋 Copy All Shares", 
                                      command=self._copy_shares, style='Secondary.TButton')
        copy_shares_button.grid(row=3, column=0, pady=(0, 0), sticky="ew")
          # Configure grid weights for responsive layout
        split_frame.columnconfigure(0, weight=1, minsize=450)  # Input column - increased minimum
        split_frame.columnconfigure(1, weight=1, minsize=500)  # Output column - increased minimum  
        split_frame.rowconfigure(1, weight=1)
        
        # Configure frame weights        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(2, weight=1)  # Text input area
        
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(2, weight=1)  # Shares display area
    
    def _create_reconstruct_tab(self):
        """Create the secret reconstruction tab with optimized compact layout."""
        reconstruct_frame = ttk.Frame(self.notebook, padding="12", style='Main.TFrame')
        self.notebook.add(reconstruct_frame, text="🔄 Reconstruct Secret")
        
        # Compact header
        header_label = ttk.Label(reconstruct_frame, text="🔄 Reconstruct Secret from Shares", 
                               font=('Segoe UI', 12, 'bold'),
                               foreground=self.colors['fg_accent'],
                               background=self.colors['bg_primary'])
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        
        # Left side - Input Section with reduced padding
        input_frame = ttk.Frame(reconstruct_frame, style='Card.TFrame', padding="15")
        input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        
        # Input section header - compact
        input_header = ttk.Label(input_frame, text="📥 Input", 
                               font=('Segoe UI', 11, 'bold'),
                               foreground=self.colors['fg_accent'],
                               background=self.colors['bg_secondary'])
        input_header.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Shares input with compact label
        shares_label = ttk.Label(input_frame, text="🔑 Enter Shares:", 
                               font=('Segoe UI', 12),
                               foreground=self.colors['fg_primary'],
                               background=self.colors['bg_secondary'])
        shares_label.grid(row=1, column=0, sticky="wn", pady=(0, 5))
        
        # Modern shares input widget
        self.shares_input_text = scrolledtext.ScrolledText(
            input_frame, height=14, width=50, wrap=tk.WORD,
            font=('Consolas', 15),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_accent'],
            selectbackground=self.colors['button_bg'],
            relief='flat',
            borderwidth=2
        )
        self.shares_input_text.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        self.sensitive_widgets.append(self.shares_input_text)
        
        # Compact instructions
        instructions_text = ("💡 Enter shares one per line (UFO strings)\n🔐 Order doesn't matter, min threshold required")
        instructions_label = ttk.Label(input_frame, text=instructions_text, 
                                     font=('Segoe UI', 10),
                                     foreground=self.colors['fg_secondary'],
                                     background=self.colors['bg_secondary'])
        instructions_label.grid(row=3, column=0, sticky="w", pady=(0, 15))
        
        # Reconstruct button
        reconstruct_button = ttk.Button(input_frame, text="🔄 Reconstruct Secret", 
                                      command=self._reconstruct_secret, style='Action.TButton')
        reconstruct_button.grid(row=4, column=0, pady=(10, 0), sticky="ew")
        
        # Right side - Output Section
        output_frame = ttk.Frame(reconstruct_frame, style='Card.TFrame', padding="20")
        output_frame.grid(row=1, column=1, sticky="nsew", padx=(15, 0), pady=(0, 20))
        
        # Output section header
        output_header = ttk.Label(output_frame, text="✨ Reconstructed Secret", style='Header.TLabel')
        output_header.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Status/instruction label
        self.reconstruct_status = ttk.Label(output_frame, 
                                           text="🔄 Your reconstructed secret will appear here",
                                             font=('Segoe UI', 10), 
                                           style='Info.TLabel')
        self.reconstruct_status.grid(row=1, column=0, sticky="w", pady=(0, 8))
        
        # Modern reconstructed secret widget
        self.reconstructed_secret_text = scrolledtext.ScrolledText(
            output_frame, height=8, width=50, wrap=tk.WORD,
            font=('Consolas', 15),
            bg=self.colors['bg_accent'],
            fg=self.colors['fg_primary'],
            insertbackground=self.colors['fg_accent'],
            selectbackground=self.colors['button_bg'],
            relief='flat',
            borderwidth=2
        )
        self.reconstructed_secret_text.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        self.sensitive_widgets.append(self.reconstructed_secret_text)
        
        # Add placeholder text
        self.reconstructed_secret_text.insert(1.0, "🔄 Waiting for shares to reconstruct...\n\n" +
                                             "Your original secret will be displayed here after successful reconstruction.")
        
        # Copy reconstructed secret button
        copy_reconstructed_button = ttk.Button(output_frame, text="📋 Copy Secret", 
                                             command=self._copy_reconstructed_secret,                                                                                      
                                             style='Secondary.TButton')
        copy_reconstructed_button.grid(row=3, column=0, pady=(0, 0), sticky="ew")
        
        # Configure grid weights for responsive layout
        reconstruct_frame.columnconfigure(0, weight=1, minsize=400)  # Input column
        reconstruct_frame.columnconfigure(1, weight=1, minsize=450)  # Output column
        reconstruct_frame.rowconfigure(1, weight=1)
        
        # Configure frame weights
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(2, weight=1)  # Shares input area
        
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(2, weight=1)  # Secret display area
    
    def _split_secret(self):
        """Split a secret into shares."""
        try:
            # Get input values
            secret = self.secret_input_text.get(1.0, tk.END).strip()
            total_shares = int(self.total_shares_var.get())
            threshold = int(self.threshold_var.get())
            
            if not secret:
                messagebox.showerror("❌ Missing Secret", "Please enter a secret to split.")
                return
            
            if threshold > total_shares:
                messagebox.showerror("❌ Invalid Parameters", 
                                   "Threshold cannot be greater than total shares.")
                return
            
            self._update_status("🔄 Splitting secret into shares...")
            
            # Split the secret
            shares = self.shamir.generate_shares(secret, total_shares, threshold)
            
            # Display the shares with clean formatting
            self.shares_text.delete(1.0, tk.END)
            
            # Update status label
            self.shares_status.config(text=f"📋 Generated {total_shares} shares ({threshold} needed to reconstruct):")
            
            # Display shares as raw Base62 strings, one per line
            shares_content = "\n\n".join(shares)
            self.shares_text.insert(1.0, shares_content)
            
            # Copy shares to clipboard automatically
            all_shares_text = "\n".join(shares)
            if safe_copy_to_clipboard(all_shares_text):
                self._update_status(f"✅ Secret split successfully! {len(shares)} shares generated and copied to clipboard.")
                
                # Auto-clear clipboard after 30 seconds for security
                def clear_clipboard():
                    time.sleep(30)
                    try:
                        safe_copy_to_clipboard("")  # Clear clipboard
                    except:
                        pass
                
                # Start clipboard clearing in background
                threading.Thread(target=clear_clipboard, daemon=True).start()
            else:
                self._update_status(f"✅ Secret split successfully! {len(shares)} shares generated (clipboard copy failed).")
            
            # Focus on the first tab to show results
            self.notebook.select(0)  # Select the first tab (Split Secret)
            
        except ValueError as e:
            messagebox.showerror("❌ Split Error", f"Failed to split secret: {str(e)}")
            self._update_status("❌ Split operation failed")
        except SecurityError as e:
            messagebox.showerror("❌ Security Error", f"Security validation failed: {str(e)}")
            self._update_status("❌ Security validation failed")
        except Exception as e:
            messagebox.showerror("❌ Unexpected Error", f"An unexpected error occurred: {str(e)}")
            self._update_status("❌ Unexpected error occurred")
    
    def _reconstruct_secret(self):
        """Reconstruct a secret from shares."""
        try:
            # Get shares input
            shares_input = self.shares_input_text.get(1.0, tk.END).strip()
            
            if not shares_input:
                messagebox.showerror("❌ Missing Shares", "Please enter shares to reconstruct the secret.")
                return
            
            self._update_status("🔄 Reconstructing secret from shares...")
            
            # Parse shares (split by lines and filter empty lines)
            shares = []
            for line in shares_input.split('\n'):
                share = line.strip()
                if share:  # Skip empty lines
                    shares.append(share)
            
            if not shares:
                messagebox.showerror("❌ No Valid Shares", "No valid shares found in input.")
                return
            
            # Validate shares before reconstruction
            valid, error = self.shamir.validate_shares(shares)
            if not valid:
                messagebox.showerror("❌ Invalid Shares", f"Share validation failed: {error}")
                return
            
            # Reconstruct the secret
            secret = self.shamir.reconstruct_secret(shares)
            
            # Display the reconstructed secret
            self.reconstructed_secret_text.delete(1.0, tk.END)
            self.reconstructed_secret_text.insert(1.0, secret)
            
            # Update status
            self.reconstruct_status.config(text=f"✅ Secret reconstructed successfully from {len(shares)} shares:")
            self._update_status(f"✅ Secret reconstructed successfully from {len(shares)} shares!")
            
        except ValueError as e:
            messagebox.showerror("❌ Reconstruction Error", f"Failed to reconstruct secret: {str(e)}")
            self._update_status("❌ Reconstruction failed")
        except Exception as e:
            messagebox.showerror("❌ Unexpected Error", f"An unexpected error occurred: {str(e)}")
            self._update_status("❌ Unexpected error occurred")
    
    def _copy_shares(self):
        """Copy all shares to clipboard."""
        shares = self.shares_text.get(1.0, tk.END).strip()
        if shares and shares != "🔄 Waiting for secret to split...":
            if safe_copy_to_clipboard(shares):
                self._update_status("📋 Shares copied to clipboard!")
            else:
                messagebox.showwarning("⚠️ Copy Failed", "Failed to copy shares to clipboard.")
        else:
            messagebox.showinfo("ℹ️ No Shares", "No shares available to copy.")
    
    def _copy_reconstructed_secret(self):
        """Copy the reconstructed secret to clipboard."""
        secret = self.reconstructed_secret_text.get(1.0, tk.END).strip()
        if secret and secret != "🔄 Waiting for shares to reconstruct...":
            if safe_copy_to_clipboard(secret):
                self._update_status("📋 Reconstructed secret copied to clipboard!")
            else:
                messagebox.showwarning("⚠️ Copy Failed", "Failed to copy secret to clipboard.")
        else:
            messagebox.showinfo("ℹ️ No Secret", "No reconstructed secret available to copy.")
    
    def _update_status(self, message: str):
        """Update the status bar with a message."""
        self.status_var.set(message)
        self.root.update_idletasks()  # Force immediate update
    
    def _clear_all_data(self):
        """Clear all sensitive data from the application."""
        result = messagebox.askyesno("🧹 Clear All Data",
                                   "This will clear all secrets, shares, and sensitive data.\n\n"
                                   "Are you sure you want to continue?")
        if result:
            # Clear all text widgets
            for widget in self.sensitive_widgets:
                widget.delete(1.0, tk.END)
            
            # Reset shares display placeholder
            self.shares_text.insert(1.0, "🔄 Waiting for secret to split...\n\n" +
                                   "Your secret shares will be displayed here as raw UFO strings.\n\n" +
                                   "Each share will be at least 250 characters long for security.")
            
            # Reset reconstructed secret placeholder
            self.reconstructed_secret_text.insert(1.0, "🔄 Waiting for shares to reconstruct...\n\n" +
                                                 "Your original secret will be displayed here after successful reconstruction.")
            
            # Reset status labels
            self.shares_status.config(text="✨ Your shares will appear here after splitting")
            self.reconstruct_status.config(text="🔄 Your reconstructed secret will appear here")
            
            # Clear crypto memory
            self.security.clear_memory()
            
            # Update status
            self._update_status("🧹 All data cleared successfully")
    
    def _on_closing(self):
        """Handle application closing."""
        # Clear sensitive data before closing
        self._clear_all_data()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()
