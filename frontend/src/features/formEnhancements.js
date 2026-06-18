/**
 * 表单验证和增强
 * 包括: 实时验证、密码强度指示、友好提示
 */

import { debounce } from './utils.js';

// ======================== 验证规则 ========================
const validationRules = {
  email: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: '请输入有效的邮箱地址'
  },
  username: {
    pattern: /^[a-zA-Z0-9_-]{3,20}$/,
    message: '用户名长度3-20个字符，只能包含字母、数字、下划线和连字符'
  },
  password: {
    minLength: 8,
    message: '密码至少8个字符'
  },
  required: {
    message: '此字段必填'
  }
};

// ======================== 密码强度检查器 ========================
class PasswordStrengthChecker {
  check(password) {
    if (!password) return { strength: 0, label: '无', feedback: [] };
    
    let strength = 0;
    const feedback = [];
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
    
    if (password.length < 8) feedback.push('至少需要8个字符');
    if (!/[A-Z]/.test(password)) feedback.push('需要至少一个大写字母');
    if (!/[a-z]/.test(password)) feedback.push('需要至少一个小写字母');
    if (!/\d/.test(password)) feedback.push('需要至少一个数字');
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) feedback.push('建议添加特殊字符');
    
    const labels = ['极弱', '较弱', '一般', '中等', '较强', '很强'];
    const label = labels[Math.min(strength, 5)] || '极弱';
    
    return { strength, label, feedback };
  }
}

const passwordChecker = new PasswordStrengthChecker();

// ======================== 实时表单验证 ========================
export function setupFormValidation() {
  const forms = document.querySelectorAll('[data-validate="true"]');
  
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      // 失焦时验证
      input.addEventListener('blur', () => validateField(input));
      
      // 输入时实时验证（防抖）
      input.addEventListener('input', debounce(() => {
        if (input.dataset.validated === 'true') {
          validateField(input);
        }
      }, 500));
    });
    
    // 表单提交前验证所有字段
    form.addEventListener('submit', (e) => {
      let isValid = true;
      inputs.forEach(input => {
        if (!validateField(input)) {
          isValid = false;
        }
        input.dataset.validated = 'true';
      });
      
      if (!isValid) {
        e.preventDefault();
        console.log('[v0] Form validation failed');
      }
    });
  });
}

// ======================== 验证单个字段 ========================
function validateField(input) {
  const name = input.name;
  const value = input.value.trim();
  const type = input.type;
  const required = input.required || input.dataset.required === 'true';
  
  // 清除之前的错误消息
  clearFieldError(input);
  
  // 必填检查
  if (required && !value) {
    showFieldError(input, validationRules.required.message);
    return false;
  }
  
  if (!value) return true; // 非必填且为空则通过
  
  // 类型特定的验证
  let isValid = true;
  let errorMessage = '';
  
  if (type === 'email') {
    isValid = validationRules.email.pattern.test(value);
    errorMessage = validationRules.email.message;
  } else if (name === 'username') {
    isValid = validationRules.username.pattern.test(value);
    errorMessage = validationRules.username.message;
  } else if (name === 'password') {
    isValid = value.length >= validationRules.password.minLength;
    errorMessage = validationRules.password.message;
  } else if (name === 'password_confirm') {
    const passwordInput = input.form?.querySelector('[name="password"]');
    isValid = value === passwordInput?.value;
    errorMessage = '两次输入的密码不一致';
  } else if (input.minLength > 0) {
    isValid = value.length >= input.minLength;
    errorMessage = `至少需要${input.minLength}个字符`;
  }
  
  if (!isValid) {
    showFieldError(input, errorMessage);
  } else {
    showFieldSuccess(input);
  }
  
  return isValid;
}

// ======================== 显示字段错误 ========================
function showFieldError(input, message) {
  input.classList.add('border-destructive', 'focus:ring-destructive/20');
  input.classList.remove('border-primary', 'focus:ring-primary/20');
  
  let errorEl = input.parentElement?.querySelector('.field-error');
  if (!errorEl) {
    errorEl = document.createElement('div');
    errorEl.className = 'field-error mt-1.5 flex items-start gap-1.5 text-sm text-destructive animate-fade-in';
    input.parentElement?.appendChild(errorEl);
  }
  
  errorEl.innerHTML = `
    <svg class="w-4 h-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
    </svg>
    <span>${message}</span>
  `;
}

// ======================== 显示字段成功 ========================
function showFieldSuccess(input) {
  input.classList.remove('border-destructive', 'focus:ring-destructive/20');
  input.classList.add('border-primary', 'focus:ring-primary/20');
  
  const errorEl = input.parentElement?.querySelector('.field-error');
  if (errorEl) {
    errorEl.remove();
  }
}

// ======================== 清除字段错误 ========================
function clearFieldError(input) {
  input.classList.remove('border-destructive', 'focus:ring-destructive/20', 'border-primary', 'focus:ring-primary/20');
  const errorEl = input.parentElement?.querySelector('.field-error');
  if (errorEl) {
    errorEl.remove();
  }
}

// ======================== 密码强度指示器 ========================
export function setupPasswordStrength() {
  const passwordInputs = document.querySelectorAll('input[name="password"]');
  
  passwordInputs.forEach(input => {
    // 创建强度指示器
    const indicator = document.createElement('div');
    indicator.className = 'mt-3 space-y-2';
    
    const strengthBar = document.createElement('div');
    strengthBar.className = 'h-2 rounded-full bg-muted overflow-hidden';
    strengthBar.innerHTML = '<div class="h-full w-0 rounded-full bg-red-500 transition-all duration-300" data-strength-fill></div>';
    
    const strengthLabel = document.createElement('div');
    strengthLabel.className = 'text-xs text-muted-foreground';
    strengthLabel.innerHTML = '强度: <span class="font-medium" data-strength-label>无</span>';
    
    const feedbackList = document.createElement('ul');
    feedbackList.className = 'text-xs text-muted-foreground space-y-0.5 list-none p-0';
    feedbackList.innerHTML = '<li data-strength-feedback style="display: none;"></li>';
    
    indicator.appendChild(strengthBar);
    indicator.appendChild(strengthLabel);
    indicator.appendChild(feedbackList);
    
    input.parentElement?.appendChild(indicator);
    
    // 监听输入
    input.addEventListener('input', () => {
      const { strength, label, feedback } = passwordChecker.check(input.value);
      
      // 更新强度条
      const fill = indicator.querySelector('[data-strength-fill]');
      const percentage = (strength / 6) * 100;
      fill.style.width = percentage + '%';
      
      // 更新颜色
      const colors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-lime-500', 'bg-green-500', 'bg-emerald-500'];
      fill.className = `h-full rounded-full transition-all duration-300 ${colors[Math.min(strength, 5)] || 'bg-red-500'}`;
      
      // 更新标签
      const labelEl = indicator.querySelector('[data-strength-label]');
      labelEl.textContent = label;
      
      // 更新反馈
      const feedbackContainer = indicator.querySelector('[data-strength-feedback]');
      if (feedback.length > 0) {
        feedbackContainer.style.display = 'block';
        feedbackContainer.innerHTML = feedback.map(f => `<li>• ${f}</li>`).join('');
      } else {
        feedbackContainer.style.display = 'none';
      }
    });
  });
}

// ======================== 表单提交反馈 ========================
export function setupFormFeedback() {
  const forms = document.querySelectorAll('form[data-feedback="true"]');
  
  forms.forEach(form => {
    const submitBtn = form.querySelector('[type="submit"]');
    if (!submitBtn) return;
    
    form.addEventListener('submit', async (e) => {
      if (form.dataset.validate === 'true') {
        // 验证表单
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;
        inputs.forEach(input => {
          if (!validateField(input)) {
            isValid = false;
          }
        });
        
        if (!isValid) {
          e.preventDefault();
          return;
        }
      }
      
      // 显示提交中状态
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="animate-spin w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
        提交中...
      `;
      
      // 表单提交后恢复
      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }, 3000);
    });
  });
}

// ======================== 初始化所有表单功能 ========================
export function initFormEnhancements() {
  setupFormValidation();
  setupPasswordStrength();
  setupFormFeedback();
  
  console.log('[v0] Form enhancements initialized');
}

export { passwordChecker };
