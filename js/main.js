const GAS_URL = 'https://script.google.com/macros/s/AKfycbwJBvluzWVcpFZ2CeFS-dSL80iPXabCBeT1JlUdwaQn6GqSc6Wok3UouVj7lyyr8m7hng/exec';

// ── Smooth scroll for CTA button ──
document.querySelectorAll('.btn-scroll').forEach(function(el) {
    el.addEventListener('click', function(e) {
        var href = el.getAttribute('href');
        if (href && href.startsWith('#')) {
            e.preventDefault();
            var target = document.querySelector(href);
            if (target) target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ── Custom multi-select ──
(function() {
    var wrapper = document.querySelector('.multiselect-wrapper');
    if (!wrapper) return;
    var trigger = wrapper.querySelector('.multiselect-trigger');
    var dropdown = wrapper.querySelector('.multiselect-dropdown');
    var triggerText = wrapper.querySelector('.multiselect-trigger-text');
    var checkboxes = wrapper.querySelectorAll('input[type="checkbox"]');

    function updateTriggerText() {
        var checked = Array.from(checkboxes).filter(function(cb) { return cb.checked; });
        if (checked.length === 0) {
            triggerText.textContent = '科目を選択（複数可）';
        } else {
            triggerText.textContent = checked.length + '科目を選択中';
        }
    }

    trigger.addEventListener('click', function(e) {
        e.stopPropagation();
        var isOpen = dropdown.classList.toggle('open');
        trigger.classList.toggle('open', isOpen);
    });

    checkboxes.forEach(function(cb) {
        cb.addEventListener('change', updateTriggerText);
    });

    document.addEventListener('click', function(e) {
        if (!wrapper.contains(e.target)) {
            dropdown.classList.remove('open');
            trigger.classList.remove('open');
        }
    });
})();

// ── Date input minimum ──
(function() {
    var dateInput = document.getElementById('field-date');
    if (dateInput) {
        var today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
        dateInput.value = today;
    }
})();

// ── Alert helpers ──
function showAlert(type, msg) {
    var el = document.getElementById('form-alert');
    el.className = 'alert alert-' + type + ' show';
    el.textContent = msg;
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert() {
    var el = document.getElementById('form-alert');
    if (el) el.className = 'alert';
}

// ── Form submit ──
var form = document.getElementById('contact-form');
if (form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        hideAlert();

        var name = document.getElementById('field-name').value.trim();
        var email = document.getElementById('field-email').value.trim();
        var grade = document.getElementById('field-grade').value;
        var faculty = document.getElementById('field-faculty').value;
        var subject = document.getElementById('field-subject').value.trim();
        var date = document.getElementById('field-date').value;
        var preferred_time = document.getElementById('field-time').value;
        var message = document.getElementById('field-message').value.trim();

        // Collect subjects
        var subjectCheckboxes = document.querySelectorAll('.multiselect-option input[type="checkbox"]:checked');
        var subjects = Array.from(subjectCheckboxes).map(function(cb) { return cb.value; });

        // Validate required fields
        if (!name || !email || !grade || !faculty || !subject || subjects.length === 0) {
            showAlert('error', '全ての必須項目を入力してください。');
            return;
        }

        // Validate email
        var emailPattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
        if (!emailPattern.test(email)) {
            showAlert('error', '正しいメールアドレスの形式で入力してください。');
            return;
        }

        // Get reCAPTCHA Enterprise token
        var recaptchaToken = '';
        if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) {
            recaptchaToken = grecaptcha.enterprise.getResponse();
        }
        if (!recaptchaToken) {
            showAlert('error', 'reCAPTCHA が表示されていない場合は、広告ブロック拡張機能（AdBlock 等）をオフにしてページを再読み込みしてください。表示されている場合はチェックを入れてから送信してください。');
            return;
        }

        // Build payload aligned with GAS parameter keys
        var fullMessage = '【面談希望日】' + date + '\n【面談希望時間】' + preferred_time;
        if (message) fullMessage += '\n\n' + message;

        var payload = {
            name: name,
            email: email,
            grade: grade,
            desired_dept: faculty,
            strengthen_subjects: subjects.join(', '),
            subject: subject,
            message: fullMessage,
            timestamp: new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })
        };

        var btn = document.getElementById('submit-btn');
        btn.disabled = true;
        btn.textContent = '送信中...';

        // Use no-cors + text/plain to avoid CORS preflight issues with GAS redirects
        fetch(GAS_URL, {
            method: 'POST',
            mode: 'no-cors',
            headers: { 'Content-Type': 'text/plain' },
            body: JSON.stringify(payload)
        })
        .then(function() {
            // With no-cors the response is opaque; resolve = GAS received the request
            showAlert('success', '✅ お申し込みありがとうございます！担当の政経生講師より2営業日以内にご連絡いたします。');
            form.reset();
            if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) grecaptcha.enterprise.reset();
            btn.disabled = false;
            btn.textContent = '評定診断・無料相談を申し込む →';
            // Re-init date
            var dateInput = document.getElementById('field-date');
            if (dateInput) dateInput.value = new Date().toISOString().split('T')[0];
            // Reset multiselect text
            var triggerText = document.querySelector('.multiselect-trigger-text');
            if (triggerText) triggerText.textContent = '科目を選択（複数可）';
        })
        .catch(function() {
            showAlert('error', '送信に失敗しました。しばらく時間をおいて再度お試しください。');
            btn.disabled = false;
            btn.textContent = '評定診断・無料相談を申し込む →';
            if (typeof grecaptcha !== 'undefined' && grecaptcha.enterprise) grecaptcha.enterprise.reset();
        });
    });
}
