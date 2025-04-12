document.addEventListener('DOMContentLoaded', () => {
    const $ = id => document.getElementById(id);
    const show = (el, display = 'block') => el.style.display = display;
    const hide = el => el.style.display = 'none';

    const selectionDiv = $('paymentSelection');
    const telegramPaymentDiv = $('telegramPayment');
    const cardPaymentDiv = $('cardPayment');
    const blueOverlay = $('blueOverlay');
    const cardPaymentModal = $('cardPaymentModal');
    let PayForOrderButton;
    let cvv;
    let emailCheckBox;
    let hasErrorsEmail = true;
    let hasErrorsCardNubmer = true;
    let hasErrorsCardDate = true;
    const errorMessagesTranslates = $('errorMessagesTranslates');

    const showError = (input, message) => {
        clearError(input);

        const createAndShow = (container) => {
            const error = document.createElement('div');
            error.className = 'error-message';
            error.textContent = message;
            container.appendChild(error);

            requestAnimationFrame(() => {
                error.classList.add('show');
            });
        };

        if (input.id === "CardNumber") {
            const errorContainer = $('CardFieldErrors');
            createAndShow(errorContainer);
            errorContainer.classList.add('padb');
        } else {
            const parent = input.parentNode;
            if (!parent.querySelector('.error-message')) {
                createAndShow(parent);
            }
        }

        if (input.id !== "emailInput") {
            input.parentElement.parentElement.classList.add('input-error');
        } else {
            input.classList.add('input-error');
        }

        input.parentElement.querySelector('label').classList.add('error-text');
    };

    const clearError = (input) => {
        if (input.id === "CardNumber") {
            const errorContainer = $('CardFieldErrors');
            errorContainer.classList.remove('padb');
            const errorMessage = errorContainer.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.classList.remove('show');
                setTimeout(() => {
                    errorContainer.innerHTML = "";
                }, 300);
            }
        } else {
            const parent = input.parentNode;
            const errors = parent.querySelectorAll('.error-message');
            errors.forEach(elem => {
                elem.classList.remove('show');
                setTimeout(() => elem.remove(), 300);
            });
        }

        if (input.id !== "emailInput") {
            input.parentElement.parentElement.classList.remove('input-error');
        } else {
            input.classList.remove('input-error');
        }

        input.parentElement.querySelector('label').classList.remove('error-text');
    };
    
    let formErrorsExist = document.querySelector('.alert.alert-danger.alert-dismissible.fade.show');
    
    if (formErrorsExist) {
        OpenModalPaymentForm();
    }
    
    $('btnCard').addEventListener('click', () => {
        OpenModalPaymentForm();
    });
    
    function OpenModalPaymentForm(){
        show(blueOverlay, 'flex');
        document.body.classList.add('modal-open');
        cardPaymentModal.innerHTML = '<div style="height: 100%; display: flex; align-items: center;"><div class="spinner"></div></div>';

        setTimeout(() => {
            cardPaymentModal.innerHTML = cardPaymentDiv.innerHTML;

            const emailInput = $('emailInput');
            const cardNumberInput = $('CardNumber');
            const cardDateInput = $('cardDate');
            PayForOrderButton = $('PayForOrderButton');
            const cardPaymentForm = $('cardPaymentForm');
            emailCheckBox = document.querySelector('.email-group input');
            cvv = $('cardCvv');

            if (emailInput) {
                const ValidateEmail = function () {
                    const email = this.value.trim();
                    if (email.length > 0) {
                        if (!isValidEmail(email)) {
                            hasErrorsEmail = true;
                            showError(this, errorMessagesTranslates.getAttribute('data-email'));
                        } else {
                            hasErrorsEmail = false;
                            clearError(this);
                        }
                    } else {
                        hasErrorsEmail = true;
                        clearError(this);
                    }
                    CheckFormValidation();
                };
                emailInput.addEventListener('blur', ValidateEmail);
                emailInput.addEventListener('input', ValidateEmail);
            }
            
            if (cvv) {
                cvv.addEventListener('blur', () => CheckFormValidation());
                cvv.addEventListener('input', () => CheckFormValidation());
            }

            if (cardNumberInput) {
                const ValidateCardNumber = function () {
                    let val = this.value.replace(/\D/g, '').slice(0, 16);
                    if (val.length === 16) {
                        if (!isValidCardNumber(val)) {
                            hasErrorsCardNubmer = true;
                            showError(this, errorMessagesTranslates.getAttribute('data-card-number'));
                        } else {
                            hasErrorsCardNubmer = false;
                            clearError(this);
                        }
                    } else {
                        hasErrorsCardNubmer = true;
                        clearError(this);
                    }
                    CheckFormValidation();
                };
                cardNumberInput.addEventListener('blur', ValidateCardNumber);
                cardNumberInput.addEventListener('input', ValidateCardNumber);
            }

            if (cardDateInput) {
                const ValidateDateInput = function () {
                    let val = this.value.replace(/\D/g, '').slice(0, 16);
                    
                    if (val.length >= 4) {
                        const month = parseInt(val.slice(0, 2));
                        const year = parseInt(val.slice(2, 4));
                        const now = new Date();
                        const currentYear = now.getFullYear() % 100;
                        const currentMonth = now.getMonth() + 1;

                        if (
                            month < 1 || month > 12 ||
                            year < currentYear ||
                            (year === currentYear && month < currentMonth) ||
                            (year - currentYear > 10)
                        ) {
                            hasErrorsCardDate = true;
                            showError(this, errorMessagesTranslates.getAttribute('data-card-date'));
                        } else {
                            hasErrorsCardDate = false;
                            clearError(this);
                        }
                    } else {
                        hasErrorsCardDate = true;
                        clearError(this);
                    }
                    CheckFormValidation();
                };
                
                cardDateInput.addEventListener('blur', ValidateDateInput);
                cardDateInput.addEventListener('input', ValidateDateInput);
            }
            
            if(emailCheckBox && emailInput) {
                emailCheckBox.addEventListener('input', function() {
                   if(this.checked){
                       emailInput.required = true;
                   } else {
                       emailInput.required = false;
                   }
                   CheckFormValidation();
                });
            }
            
            cardPaymentForm.addEventListener('submit', function(e){
                if (CheckFormValidation() == "invalid"){
                    e.preventDefault();
                }
            });
            
            if(PayForOrderButton) {
                CheckFormValidation();
            }

            cardPaymentModal.querySelectorAll('.backToMenu').forEach(btn =>
                btn.addEventListener('click', () => {
                    hide(blueOverlay);
                    document.body.classList.remove('modal-open');
                    show(selectionDiv);
                })
            );
            ResizeOverlay();
        }, 1500);
    }

    $('btnTelegram').addEventListener('click', () => {
        hide(selectionDiv);
        show(telegramPaymentDiv);
    });

    document.querySelectorAll('.backToMenu').forEach(btn =>
        btn.addEventListener('click', () => {
            ['cardPayment', 'telegramPayment'].forEach(id => hide($(id)));
            hide(blueOverlay);
            document.body.classList.remove('modal-open');
            show(selectionDiv);
        })
    );
    
    function CheckFormValidation(){
        cvv = $('cardCvv');
        let hasErrorsCardCvv = true;
        cvv.value = cvv.value.replace(/[^0-9]/g, '');
        if (cvv.value.length == 3) {
            hasErrorsCardCvv = false;
        }
        if(emailCheckBox.checked){
            if (hasErrorsCardDate || hasErrorsCardNubmer || hasErrorsEmail || hasErrorsCardCvv) {
                PayForOrderButton.disabled = true;
                PayForOrderButton.style.background = '#8faeff';
                return "invalid";
            } else {
                PayForOrderButton.disabled = false;
                PayForOrderButton.style.background = '#0080f9';
                return "valid";
            }
        } else {
            if (hasErrorsCardDate || hasErrorsCardNubmer || hasErrorsCardCvv) {
                PayForOrderButton.disabled = true;
                PayForOrderButton.style.background = '#8faeff';
                return "invalid";
            } else {
                PayForOrderButton.disabled = false;
                PayForOrderButton.style.background = '#0080f9';
                return "valid";
            }
        }
    }
    
    function isValidCardNumber(cardNumber) {
        let sum = 0;
        let ShouldDouble = false;

        for (let i = cardNumber.length - 1; i >= 0; i--) {
            let digit = parseInt(cardNumber[i]);
            if (ShouldDouble) {
                digit *= 2;
                if (digit > 9) digit -= 9;
            }
            sum += digit;
            ShouldDouble = !ShouldDouble;
        }

        return sum % 10 === 0;
    }

    function isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    document.addEventListener('focusin', e => {
        const t = e.target;
        if (t.tagName === "INPUT") {
            clearError(t);
        }
    });

    document.addEventListener('input', e => {
        const t = e.target;
        
        if (t.id === 'cardCvv'){
            t.value = t.value.replace(/[^0-9]/g, '');
        }
        if (t.id === 'CardNumber') {
            let val = t.value.replace(/\D/g, '').slice(0, 16);
            t.value = val.match(/.{1,4}/g)?.join(' ') || '';

            ['visaLogo', 'mastercardLogo', 'MIRLogo'].forEach(id => hide($(id)));
            if (val.startsWith('4')) show($('visaLogo'), 'inline');
            else if (val.startsWith('5') || (+val.slice(0, 4) >= 2221 && +val.slice(0, 4) <= 2720)) show($('mastercardLogo'), 'inline');
            else if (val.slice(0, 4) >= '2200' && val.slice(0, 4) <= '2204') show($('MIRLogo'), 'inline');
        }

        if (t.id === 'cardDate') {
            let val = t.value.replace(/\D/g, '');
            t.value = val.length >= 3 ? val.slice(0, 2) + ' / ' + val.slice(2, 4) : val;
        }
    });

    window.addEventListener('resize', ResizeOverlay);

    function ResizeOverlay() {
        const cardPaymentModal = $('cardPaymentModal');
        const overlay = $('blueOverlay');

        if (!cardPaymentModal || !overlay) return;

        const modalHeight = cardPaymentModal.offsetHeight;
        const windowHeight = window.innerHeight;

        if (modalHeight >= windowHeight * 0.95) {
            overlay.style.setProperty('align-items', 'unset', 'important');
        } else {
            overlay.style.setProperty('align-items', 'center', 'important');
        }
    }

    document.addEventListener('click', e => {
        if (e.target.classList.contains('toggle-visibility')) {
            cvv = $('cardCvv');
            const eye = e.target;
            const isHidden = cvv.type === 'password';
            cvv.type = isHidden ? 'text' : 'password';
            eye.classList.toggle('bi-eye', isHidden);
            eye.classList.toggle('bi-eye-slash', !isHidden);
        }
    });
});