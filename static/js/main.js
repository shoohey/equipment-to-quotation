/**
 * 機器表→見積書 自動生成システム - メインJS
 */

document.addEventListener('DOMContentLoaded', function () {
    initUpload();
    initEditableTable();
});

/* =======================
   アップロード機能
   ======================= */
function initUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadForm = document.getElementById('uploadForm');
    const demoForm = document.getElementById('demoForm');

    if (!uploadArea) return;

    // クリックでファイル選択
    uploadArea.addEventListener('click', function () {
        fileInput.click();
    });

    // ドラッグ&ドロップ
    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function () {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            showFileInfo(files[0]);
        }
    });

    // ファイル選択
    fileInput.addEventListener('change', function () {
        if (fileInput.files.length > 0) {
            showFileInfo(fileInput.files[0]);
        }
    });

    function showFileInfo(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'xlsx' && ext !== 'xls') {
            alert('Excel形式（.xlsx, .xls）のファイルを選択してください。');
            return;
        }
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
    }

    // アップロード送信時
    if (uploadForm) {
        uploadForm.addEventListener('submit', function () {
            showAnalyzing();
        });
    }

    // デモ送信時
    if (demoForm) {
        demoForm.addEventListener('submit', function () {
            showAnalyzing();
        });
    }
}

/* =======================
   AI解析アニメーション
   ======================= */
function showAnalyzing() {
    const overlay = document.getElementById('analyzingOverlay');
    const progress = document.getElementById('analyzingProgress');
    const text = document.getElementById('analyzingText');
    if (!overlay) return;

    overlay.classList.add('active');

    const messages = [
        'AI が機器表を解析しています...',
        '品番を認識しています...',
        '商品マスタと照合中...',
        '数量を集計しています...',
        'データを整理しています...',
    ];

    let step = 0;
    const interval = setInterval(function () {
        step++;
        const pct = Math.min(step * 20, 95);
        progress.style.width = pct + '%';
        if (step < messages.length) {
            text.textContent = messages[step];
        }
    }, 500);
}

/* =======================
   テーブル編集機能
   ======================= */
function initEditableTable() {
    const editableCells = document.querySelectorAll('.editable');
    if (editableCells.length === 0) return;

    editableCells.forEach(function (cell) {
        cell.addEventListener('dblclick', function () {
            if (cell.querySelector('input')) return;

            const originalValue = cell.textContent.trim();
            const field = cell.dataset.field;
            const input = document.createElement('input');
            input.type = field === 'quantity' ? 'number' : 'text';
            input.value = originalValue;
            input.className = 'edit-input';

            cell.textContent = '';
            cell.appendChild(input);
            input.focus();
            input.select();

            function saveEdit() {
                const newValue = input.value.trim();
                cell.textContent = newValue || originalValue;
                updateEquipmentData(cell, field, newValue);
            }

            input.addEventListener('blur', saveEdit);
            input.addEventListener('keydown', function (e) {
                if (e.key === 'Enter') {
                    input.blur();
                } else if (e.key === 'Escape') {
                    cell.textContent = originalValue;
                }
            });
        });
    });
}

function updateEquipmentData(cell, field, value) {
    const row = cell.closest('tr');
    const index = row.dataset.index;
    const dataInput = document.getElementById('equipmentData');
    if (!dataInput || index === undefined) return;

    try {
        const data = JSON.parse(dataInput.value);
        if (data.items && data.items[index]) {
            if (field === 'quantity') {
                data.items[index][field] = parseInt(value) || 0;
            } else {
                data.items[index][field] = value;
            }
            dataInput.value = JSON.stringify(data);
        }
    } catch (e) {
        console.error('データ更新エラー:', e);
    }
}
