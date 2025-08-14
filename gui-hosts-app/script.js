class HostsGeneratorApp {
    constructor() {
        this.extensions = [];
        this.downloadInterval = null;
        this.currentLanguage = 'es';
        this.strings = {};
        this.init();
    }

    async init() {
        // Esperar a que pywebview esté disponible
        await this.waitForPywebview();
        await this.loadLanguage(this.currentLanguage);
        this.setupEventListeners();
        this.updateLastUpdateTime();
        await this.checkSourcesStatus();
    }

    async waitForPywebview() {
        return new Promise((resolve) => {
            const checkPywebview = () => {
                if (window.pywebview && window.pywebview.api) {
                    resolve();
                } else {
                    setTimeout(checkPywebview, 100);
                }
            };
            checkPywebview();
        });
    }

    setupEventListeners() {
        document.getElementById('download-btn').addEventListener('click', () => this.downloadSources());
        document.getElementById('update-btn').addEventListener('click', () => this.updateSources());
        document.getElementById('language-selector').addEventListener('change', (e) => this.changeLanguage(e.target.value));
    }

    async loadLanguage(langCode) {
        try {
            this.strings = await pywebview.api.get_language_strings(langCode);
            this.currentLanguage = langCode;
            this.updateUI();
            document.getElementById('language-selector').value = langCode;
        } catch (error) {
            console.error('Error loading language:', error);
        }
    }

    async changeLanguage(langCode) {
        await this.loadLanguage(langCode);
        this.showNotification(this.getString('data_updated'), 'success');
    }

    getString(key, params = {}) {
        let str = this.strings[key] || key;
        Object.keys(params).forEach(param => {
            str = str.replace(`{${param}}`, params[param]);
        });
        return str;
    }

    updateUI() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.getString(key);
        });
        
        // Actualizar placeholders y otros textos dinámicos
        if (this.extensions.length > 0) {
            this.renderExtensions();
        }
    }

    updateLastUpdateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('last-update').innerHTML = `${this.getString('last_update')}: ${timeString}`;
    }

    async checkSourcesStatus() {
        try {
            const status = await pywebview.api.check_sources_exist();
            const sourcesStep = document.getElementById('sources-step');
            const sourcesStatus = document.getElementById('sources-status');
            const downloadBtn = document.getElementById('download-btn');
            const updateBtn = document.getElementById('update-btn');
            
            if (status.all_exist) {
                sourcesStep.className = 'step-card success';
                sourcesStatus.textContent = `${this.getString('all_sources_available')} (${status.existing}/${status.total})`;
                downloadBtn.style.display = 'none';
                updateBtn.style.display = 'inline-flex';
                this.showExtensionsSection();
            } else {
                sourcesStep.className = 'step-card warning';
                sourcesStatus.textContent = `${this.getString('missing_sources', {count: status.missing.length})}: ${status.missing.join(', ')}`;
                downloadBtn.style.display = 'inline-flex';
                updateBtn.style.display = 'none';
            }
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
        }
    }

    async downloadSources() {
        await this.performDownload('download_sources_async', this.getString('downloading'));
    }

    async updateSources() {
        await this.performDownload('update_sources_async', this.getString('downloading'));
    }

    async performDownload(apiMethod, buttonText) {
        const downloadBtn = document.getElementById('download-btn');
        const updateBtn = document.getElementById('update-btn');
        const progressDiv = document.getElementById('download-progress');
        
        downloadBtn.disabled = true;
        updateBtn.disabled = true;
        downloadBtn.innerHTML = `<span class="loading"></span> ${buttonText}`;
        updateBtn.innerHTML = `<span class="loading"></span> ${buttonText}`;
        progressDiv.style.display = 'block';

        try {
            await pywebview.api[apiMethod]();
            
            this.downloadInterval = setInterval(async () => {
                const status = await pywebview.api.get_download_status();
                
                document.getElementById('download-message').textContent = status.current_source;
                document.getElementById('progress-fill').style.width = status.progress + '%';
                document.getElementById('progress-text').textContent = status.progress + '%';
                
                if (!status.downloading) {
                    clearInterval(this.downloadInterval);
                    
                    if (status.progress === 100) {
                        const message = apiMethod === 'update_sources_async' ? 
                            this.getString('sources_updated') : this.getString('sources_downloaded');
                        this.showNotification(message, 'success');
                        setTimeout(() => this.checkSourcesStatus(), 1000);
                    } else {
                        this.showNotification(this.getString('download_error') + ': ' + status.message, 'error');
                    }
                    
                    downloadBtn.disabled = false;
                    updateBtn.disabled = false;
                    downloadBtn.innerHTML = this.getString('download_sources');
                    updateBtn.innerHTML = this.getString('update_sources');
                    progressDiv.style.display = 'none';
                }
            }, 250);
            
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
            downloadBtn.disabled = false;
            updateBtn.disabled = false;
            downloadBtn.innerHTML = this.getString('download_sources');
            updateBtn.innerHTML = this.getString('update_sources');
            progressDiv.style.display = 'none';
        }
    }

    async showExtensionsSection() {
        document.getElementById('extensions-section').classList.remove('hidden');
        document.getElementById('generate-section').classList.remove('hidden');
        await this.loadExtensions();
        this.loadOutputFiles();
    }

    async loadExtensions() {
        try {
            this.extensions = await pywebview.api.get_available_extensions();
            this.renderExtensions();
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
        }
    }

    renderExtensions() {
        const grid = document.getElementById('extensions-grid');
        grid.innerHTML = '';

        // Ordenar extensiones: base primero, luego el resto
        const sortedExtensions = this.extensions.sort((a, b) => {
            if (a.is_base) return -1;
            if (b.is_base) return 1;
            return a.name.localeCompare(b.name);
        });

        sortedExtensions.forEach(ext => {
            const card = document.createElement('div');
            const cardClasses = ['extension-card'];
            
            if (!ext.available) cardClasses.push('unavailable');
            if (ext.is_base) cardClasses.push('base-extension');
            
            card.className = cardClasses.join(' ');
            
            // Convertir tamaño a MB
            const sizeText = ext.available ? `${(ext.size / (1024 * 1024)).toFixed(2)} MB` : this.getString('not_available');
            const statusText = ext.available ? this.getString('available') : this.getString('missing');
            
            card.innerHTML = `
                <div class="extension-header">
                    <input type="checkbox" class="extension-checkbox" id="ext-${ext.name}" ${ext.available ? '' : 'disabled'} ${ext.is_base ? 'checked' : ''}>
                    <span class="extension-name">${ext.name}</span>
                    ${ext.is_base ? '<span class="base-badge">BASE</span>' : ''}
                </div>
                <div class="extension-description">${this.getExtensionDescription(ext.name)}</div>
                <div class="extension-stats">
                    <span>📊 ${sizeText}</span>
                    <span>${statusText}</span>
                </div>
            `;
            
            if (ext.available) {
                if (ext.is_base) {
                    card.classList.add('selected');
                    card.addEventListener('click', () => {
                        const checkbox = card.querySelector('input');
                        checkbox.checked = !checkbox.checked;
                        card.classList.toggle('selected', checkbox.checked);
                    });
                } else {
                    card.addEventListener('click', () => {
                        const checkbox = card.querySelector('input');
                        checkbox.checked = !checkbox.checked;
                        card.classList.toggle('selected', checkbox.checked);
                    });
                }
            }
            
            grid.appendChild(card);
        });
    }

    getExtensionDescription(name) {
        const descriptions = {
            'base': this.getString('base_hosts_desc'),
            'fakenews': this.getString('fakenews_desc'),
            'gambling': this.getString('gambling_desc'),
            'porn': this.getString('porn_desc'),
            'social': this.getString('social_desc')
        };
        return descriptions[name] || name;
    }

    selectAllExtensions() {
        document.querySelectorAll('.extension-checkbox:not(:disabled)').forEach(checkbox => {
            checkbox.checked = true;
            checkbox.closest('.extension-card').classList.add('selected');
        });
    }

    clearAllExtensions() {
        document.querySelectorAll('.extension-checkbox:not([id="ext-base"])').forEach(checkbox => {
            checkbox.checked = false;
            checkbox.closest('.extension-card').classList.remove('selected');
        });
        // Mantener base seleccionado
        const baseCheckbox = document.getElementById('ext-base');
        if (baseCheckbox) {
            baseCheckbox.checked = false;
            baseCheckbox.closest('.extension-card').classList.add('selected');
        }
    }

    async generateHostsFile() {
        const selectedExtensions = [];
        document.querySelectorAll('.extension-checkbox:checked').forEach(checkbox => {
            selectedExtensions.push(checkbox.id.replace('ext-', ''));
        });

        if (selectedExtensions.length === 0) {
            this.showNotification(this.getString('select_extension_warning'), 'warning');
            return;
        }

        const generateBtn = document.getElementById('generate-btn');
        generateBtn.disabled = true;
        generateBtn.innerHTML = `<span class="loading"></span> ${this.getString('generating')}`;

        try {
            const result = await pywebview.api.generate_hosts_file(selectedExtensions);
            
            if (result.success) {
                this.showNotification(`${this.getString('file_generated')}: ${result.filename}`, 'success');
                this.loadOutputFiles();
            } else {
                this.showNotification(this.getString('error') + ': ' + result.message, 'error');
            }
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
        } finally {
            generateBtn.disabled = false;
            generateBtn.innerHTML = this.getString('generate_button');
        }
    }

    async loadOutputFiles() {
        try {
            const files = await pywebview.api.get_output_files();
            const container = document.getElementById('output-files');
            
            if (files.length === 0) {
                container.innerHTML = `
                    <div class="file-item">
                        <div class="file-info">
                            <span>📄</span>
                            <div>
                                <div class="file-name">${this.getString('no_files_generated')}</div>
                                <div class="file-meta">${this.getString('generate_first_file')}</div>
                            </div>
                        </div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = files.map(file => {
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                return `
                    <div class="file-item">
                        <div class="file-info">
                            <span>📄</span>
                            <div>
                                <div class="file-name">${file.name}</div>
                                <div class="file-meta">${file.modified} • ${sizeMB} MB</div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
        }
    }

    async openOutputFolder() {
        try {
            await pywebview.api.open_output_folder();
        } catch (error) {
            this.showNotification(this.getString('error') + ': ' + error.message, 'error');
        }
    }

    async refreshAll() {
        this.updateLastUpdateTime();
        await this.checkSourcesStatus();
        if (this.extensions.length > 0) {
            await this.loadExtensions();
        }
        await this.loadOutputFiles();
        this.showNotification(this.getString('data_updated'), 'success');
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);
    }
}

// Crear instancia global de la aplicación
let app;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    app = new HostsGeneratorApp();
});