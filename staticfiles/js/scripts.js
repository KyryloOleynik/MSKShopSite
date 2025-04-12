import { GoogleGenerativeAI } from "@google/generative-ai";

document.addEventListener("DOMContentLoaded", function() {
    let chatHistory = [];
    const chatBox = document.getElementById("chatBox");
    
    document.getElementById("chat_icon").addEventListener("click", toggleChatMenu);
    document.getElementById("openChatBut").addEventListener("click", openChat);
    document.getElementById("closeChatBut").addEventListener("click", closeChat);
    const chatInput = document.getElementById("chatInput");
    
    function toggleChatMenu() {
        document.getElementById("chatMenu").classList.toggle("d-none");
        document.getElementById("chat_icon").classList.toggle("d-none");
    }
    
    function openChat() {
        document.getElementById("chatMenu").classList.add("d-none");
        chatBox.classList.remove("d-none");
        setTimeout(() => {
            document.getElementById("start-message").classList.remove("d-none");
        }, 600);
    }
    
    function closeChat() {
        chatBox.classList.add("d-none");
        document.getElementById("chat_icon").classList.remove("d-none");
    }
    
    document.getElementById("sendMessageBtn").addEventListener("click", () => {
        if (chatInput.value.trim() !== "") {
            sendUserMessage(chatInput.value);
            chatInput.value = "";
        }
    });
    
    chatInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            if (chatInput.value.trim() !== "") {
                sendUserMessage(chatInput.value);
                chatInput.value = "";
            }
        }
    });
    
    async function GeminiResponse(userMessage) {
        const API_KEY = "AIzaSyBUWu0VEl7y7bC5u043RAsh5Q6pEiyw8Hw";
        const genAI = new GoogleGenerativeAI(API_KEY);
        const model = genAI.getGenerativeModel({
            model: "gemini-2.0-flash-lite-preview-02-05",
            systemInstruction: "Ты – консультант по имени Саня, работающий в интернет-магазине MSK Shop, который специализируется на продаже новых оригинальных товаров из Европы. Наш магазин предлагает товары высокого качества по доступным ценам – в среднем на 30-35% ниже рыночных благодаря сотрудничеству с поставщиками и поиску выгодных предложений на платформах вроде Avito и eBay. Все товары новые, запечатанные, с чеком, подтверждающим их подлинность.  Мы осуществляем быструю доставку: по Москве – 3-4 дня, по Росии в зависимости от региона до двух недель, по Берлину – 4-5 дней. Важно отметить, что возвраты возможны в течение 14 дней при сохранении товарного вида и упаковки, в соответствии с Законом РФ «О защите прав потребителей». Мы также предоставляем гарантию на товары и право на возврат средств при обнаружении дефектов.Помни, что магазин ориентирован на клиента – помогай кратко, профессионально и дружелюбно. Подчеркивай низкие цены, качество товаров и прозрачные условия доставки. Если пользователь нуждается в дополнительной помощи, предложи связаться с реальной техподдержкой через Telegram или емейл support@msk52.shop. Отвечай всегда на языке пользователя и акцентируй внимание на уникальных преимуществах MSK Shop.",
            generationConfig: {}
        });
    
        const chat = model.startChat({ history: chatHistory });
    
        const result = await chat.sendMessage(userMessage);
        const response = await result.response;
        const text = await response.text();
    
        chatHistory.push({ role: "model", parts: [{ text }] });
        addBotMessage(text);
    }
    
    function addBotMessage(message) {
        let chatBoxBody = document.querySelector("#chatBox .card-body");
        chatBoxBody.innerHTML += `<p class='card p-2'><strong>Консультант:</strong> ${message}</p>`;
    }
    
    function sendUserMessage(message) {
        let chatBoxBody = document.querySelector("#chatBox .card-body");
        if (chatBoxBody) {
            chatBoxBody.innerHTML += `<p class='card p-2 text-end'><strong>Вы:</strong> ${message}</p>`;
        }
    
        chatHistory.push({ role: "user", parts: [{ text: message }] });
        GeminiResponse(message);
    }
    
    let imageElements = document.querySelectorAll(".product-image");

    if (imageElements) {
        imageElements.forEach(imageElement => {
            let defaultSrc = imageElement.src;
            let hoverSrc = imageElement.getAttribute("data-hover");
    
            imageElement.addEventListener("mouseenter", function() {
                imageElement.src = hoverSrc;
            });
    
            imageElement.addEventListener("mouseleave", function() {
                imageElement.src = defaultSrc;
            });
        });
    }

    const params = new URLSearchParams(window.location.search);
    
    if (params.has("cartopen")) {
        let modal = new bootstrap.Modal(document.getElementById("cartModal"));
        modal.show();

        params.delete('cartopen');
        const newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
        window.history.replaceState({}, document.title, newUrl);
    }
    
    if (params.has("order_id")){
        let modal = new bootstrap.Modal(document.getElementById("orderModal"));
        modal.show();

        params.delete('order_id');
        const newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
        window.history.replaceState({}, document.title, newUrl);
    }
    
    const nextButtons = document.querySelectorAll("button[data-bs-toggle='tab']");
            
    nextButtons.forEach(button => {
        button.addEventListener("click", function () {
            const target = document.querySelector(this.getAttribute("data-bs-target"));
            updateConfirmation();
        });
    });
    
    document.querySelectorAll("[data-next-tab]").forEach(button => {
        button.addEventListener("click", function () {
            let nextTab = this.getAttribute("data-next-tab");
            let tabElement = document.querySelector(`#${nextTab}-tab`); // Исправлено
    
            if (tabElement) {
                let tab = new bootstrap.Tab(tabElement);
                tab.show();
            }
            updateConfirmation();
        });
    });

    const deliveryMethodSelect = document.getElementById("id_delivery_method");
    const prepaymentInput = document.getElementById("prepayment");
    const paymentMethodInput = document.getElementById("id_payment_method");
    const delivery_cost_text = document.getElementById("delivery_cost");
    const totalPriceOrder = document.getElementById("totalPriceOrder");
    totalPriceOrder.innerText = totalPriceOrder.getAttribute("data-cart-total") + " + " + prepaymentInput.getAttribute("data-price-low");

    function updatePrepayment() {
        if (!deliveryMethodSelect || !prepaymentInput) return;

        const selectedDelivery = deliveryMethodSelect.value;
        const selectedPayment = paymentMethodInput.value;

        if (selectedDelivery == "Сourier (Only for Moscow and Berlin)") {
            if (selectedPayment === "On card" || selectedPayment === "Crypto") {
                prepaymentInput.placeholder = prepaymentInput.getAttribute("data-price-courier"); 
                delivery_cost_text.innerText = prepaymentInput.getAttribute("data-price-courier-low");
                totalPriceOrder.innerText = totalPriceOrder.getAttribute("data-cart-total") + " + " + prepaymentInput.getAttribute("data-price-courier-low");
            } else {
                prepaymentInput.placeholder = prepaymentInput.getAttribute("data-price-courier-low"); 
                delivery_cost_text.innerText = prepaymentInput.getAttribute("data-price-courier-low");
                totalPriceOrder.innerText = totalPriceOrder.getAttribute("data-cart-total") + " + " + prepaymentInput.getAttribute("data-price-courier-low");
            }
        } else {
            if (selectedPayment === "On card" || selectedPayment === "Crypto") {
                prepaymentInput.placeholder = prepaymentInput.getAttribute("data-price"); 
                delivery_cost_text.innerText = prepaymentInput.getAttribute("data-price-low");
                totalPriceOrder.innerText = totalPriceOrder.getAttribute("data-cart-total") + " + " + prepaymentInput.getAttribute("data-price-low");
            } else {
                prepaymentInput.placeholder = prepaymentInput.getAttribute("data-price-low"); 
                delivery_cost_text.innerText = prepaymentInput.getAttribute("data-price-low");
                totalPriceOrder.innerText = totalPriceOrder.getAttribute("data-cart-total") + " + " + prepaymentInput.getAttribute("data-price-low");
            }
        }

        updateConfirmation();
    }

    if (deliveryMethodSelect) {
        deliveryMethodSelect.addEventListener("change", updatePrepayment);
    }

    const paymentCards = document.querySelectorAll('.payment-card');
    paymentCards.forEach(card => {
        card.addEventListener("click", function () {
            paymentCards.forEach(c => c.classList.remove('border', 'border-primary'));
            card.classList.add('border', 'border-primary');

            paymentMethodInput.value = card.getAttribute('data-value');
            updatePrepayment();
        });
    });

    function updateConfirmation() {
        document.getElementById("confirmPhone_number").innerText = (document.getElementById("id_phone_number")?.value || "");
        document.getElementById("confirmFullName").innerText =
            (document.getElementById("id_last_name")?.value || "") + " " +
            (document.getElementById("id_first_name")?.value || "") + " " +
            (document.getElementById("id_patronymic")?.value || "");
        document.getElementById("confirmAddress").innerText = (document.getElementById("id_order_adress")?.value || "");
        document.getElementById("confirmDelivery").innerText = (deliveryMethodSelect?.value || "");
        document.getElementById("confirmPayment").innerText = (paymentMethodInput?.value || "");
        document.getElementById("confirmPrepayment").innerText = (prepaymentInput?.placeholder || "");
    }

    updatePrepayment();
});