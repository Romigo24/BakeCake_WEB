const { Form: VForm, Field: VField, ErrorMessage } = VeeValidate;

Vue.createApp({
  name: "App",
  components: { VForm, VField, ErrorMessage },

  data() {
    return {
      apiBaseAddress: `${window.location.origin}/api/v1`,

      schema1: {
        lvls: (value) => (value ? true : " количество уровней"),
        form: (value) => (value ? true : " форму торта"),
        topping: (value) => (value ? true : " топпинг"),
      },
      GDPRConsent: false,
      schema2: {
        name: (value) => (value ? true : " имя"),
        phone: (value) => (value ? true : " телефон"),
        name_format: (value) => (!value || /^[a-zA-Zа-яА-Я]+$/.test(value) ? true : "⚠ Формат имени нарушен"),
        email_format: (value) => (!value || /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value) ? true : "⚠ Формат почты нарушен"),
        phone_format: (value) => (!value || /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/.test(value) ? true : "⚠ Формат телефона нарушен"),
        email: (value) => (value ? true : " почту"),
        address: (value) => (value ? true : " адрес"),
        date: (value) => (value ? true : " дату доставки"),
        time: (value) => (value ? true : " время доставки"),
        gdpr: (value) => (value ? true : " политику конфиденциальности"),
      },

      DATA: { Levels: [], Forms: [], Toppings: [], Berries: [], Decors: [] },
      Costs: { Levels: [], Forms: [], Toppings: [], Berries: [], Decors: [], Words: 0 },

      Levels: 0,
      Form: 0,
      Topping: 0,
      Berries: 0,
      Decor: 0,
      Words: "",
      Comments: "",
      Designed: false,

      Name: "",
      Phone: null,
      Email: null,
      Address: null,
      Dates: null,
      Time: null,
      DelivComments: "",

      optionsLoadingInProgress: true,
      orderSubmittingInProgress: false,
    };
  },

  async mounted() {
    await this.fetchCatalogOptions();
    this.optionsLoadingInProgress = false;
  },

  computed: {
    Cost() {
      if (this.optionsLoadingInProgress) return 0;
      const getPriceByIndex = (list, index) => (Array.isArray(list) && list[index] != null ? Number(list[index]) : 0);
      const inscriptionPrice = (this.Words || "").trim() ? Number(this.Costs.Words || 0) : 0;
      return (
        getPriceByIndex(this.Costs.Levels, Number(this.Levels)) +
        getPriceByIndex(this.Costs.Forms, Number(this.Form)) +
        getPriceByIndex(this.Costs.Toppings, Number(this.Topping)) +
        getPriceByIndex(this.Costs.Berries, Number(this.Berries)) +
        getPriceByIndex(this.Costs.Decors, Number(this.Decor)) +
        inscriptionPrice
      );
    },
  },

  methods: {
    ToStep4() {
      this.Designed = true;
      setTimeout(() => this.$refs.ToStep4.click(), 0);
    },

    async fetchCatalogOptions() {
      const response = await fetch(`${this.apiBaseAddress}/catalog/options/`, { headers: { Accept: "application/json" } });
      if (!response.ok) return;
      const optionsPayload = await response.json();

      this.DATA.Levels   = optionsPayload.levels.values;
      this.DATA.Forms    = optionsPayload.forms.values;
      this.DATA.Toppings = optionsPayload.toppings.values;
      this.DATA.Berries  = optionsPayload.berries.values;
      this.DATA.Decors   = optionsPayload.decors.values;

      this.Costs.Levels   = optionsPayload.levels.prices;
      this.Costs.Forms    = optionsPayload.forms.prices;
      this.Costs.Toppings = optionsPayload.toppings.prices;
      this.Costs.Berries  = optionsPayload.berries.prices;
      this.Costs.Decors   = optionsPayload.decors.prices;
      this.Costs.Words    = optionsPayload.words_price;

      this.Levels = 0;
      this.Form = 0;
      this.Topping = 0;
      this.Berries = 0;
      this.Decor = 0;
    },

    buildOrderPayload() {
      return {
        LEVELS: String(this.Levels ?? "0"),
        FORM: String(this.Form ?? "0"),
        TOPPING: String(this.Topping ?? "0"),
        BERRIES: String(this.Berries ?? "0"),
        DECOR: String(this.Decor ?? "0"),
        WORDS: (this.Words || "").trim(),
        COMMENTS: (this.Comments || "").trim(),
        NAME: (this.Name || "").trim(),
        PHONE: (this.Phone || "").trim(),
        EMAIL: (this.Email || "").trim(),
        ADDRESS: (this.Address || "").trim(),
        DATE: this.Dates || "",
        TIME: this.Time || "",
        DELIVCOMMENTS: (this.DelivComments || "").trim(),
        CLIENT_TOTAL: this.Cost,
      };
    },

    async submitOrder() {
        if (this.orderSubmittingInProgress) return;
        this.orderSubmittingInProgress = true;

        try {
            if (!this.GDPRConsent) {
                this.orderSubmittingInProgress = false;
                alert("Для оформления заказа необходимо согласие на обработку персональных данных");
                return;
            }

            if (this.Dates && this.Time) {
                const validation = await this.validateDeliveryTime(this.Dates, this.Time);
                if (!validation.valid) {
                    this.orderSubmittingInProgress = false;
                    alert(`Ошибка времени доставки: ${validation.reason}`);
                    return;
                }
            }

            const payload = this.buildOrderPayload();
        
            console.log("Sending order payload:", payload);

            const response = await fetch(`${this.apiBaseAddress}/orders/create/`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json", 
                    Accept: "application/json" 
                },
                body: JSON.stringify(payload),
            });

            let responseBody = {};
            try { 
                responseBody = await response.json(); 
            } catch (jsonError) {
                console.error("JSON parse error:", jsonError);
            }

            this.orderSubmittingInProgress = false;

            switch (response.status) {
                case 201:
                    this.handleSuccessResponse(responseBody);
                    break;
                
                case 409:
                    this.handlePriceConflict(responseBody, payload);
                    break;
                
                case 400:
                    this.handleValidationErrors(responseBody);
                    break;
                
                case 500:
                    this.handleServerError(responseBody);
                    break;
                
                default:
                    this.handleUnknownError(response, responseBody);
            }

        } catch (networkError) {
            this.orderSubmittingInProgress = false;
            console.error("Network error:", networkError);
            alert("Ошибка сети. Проверьте подключение к интернету и попробуйте снова.");
        }
    },

    handleSuccessResponse(responseBody) {
        let message = `🎉 Заказ оформлен успешно!\nНомер заказа: #${responseBody.order_id}`;
    
        if (responseBody.is_urgent) {
            message += `\n⚡ Срочный заказ! Наценка за срочность: +${responseBody.urgent_surcharge}₽`;
        }
    
        message += `\n💰 Общая стоимость: ${responseBody.total}₽`;
    
        if (responseBody.delivery_date && responseBody.delivery_time) {
            const deliveryDate = new Date(responseBody.delivery_date);
            const deliveryTime = responseBody.delivery_time.substring(0, 5);
            message += `\n📅 Дата доставки: ${deliveryDate.toLocaleDateString('ru-RU')} в ${deliveryTime}`;
        }
    
        message += `\n📊 Статус: ${this.getStatusText(responseBody.status)}`;
        message += `\n\nСпасибо за заказ! С вами свяжутся для подтверждения.`;

        alert(message);
    
        this.resetOrderForm();
    
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    handlePriceConflict(responseBody, payload) {
        let message = `💰 Цена изменилась!\nНовая цена: ${responseBody.server_total}₽`;
    
        if (responseBody.is_urgent !== undefined) {
            message += responseBody.is_urgent ? 
                "\n⚡ Включена наценка за срочную доставку (+20%)" : 
                "\n⏱️ Обычная доставка (без наценки)";
        }
    
        if (confirm(message + "\n\nПродолжить оформление заказа с новой ценой?")) {
            this.Cost = responseBody.server_total;
            setTimeout(() => this.submitOrder(), 100);
        }
    },

    handleValidationErrors(responseBody) {
        let errorMessage = "❌ Пожалуйста, исправьте ошибки в форме:\n";
    
        if (typeof responseBody === 'object' && responseBody !== null) {
            for (const [field, messages] of Object.entries(responseBody)) {
                const fieldName = this.getFieldName(field);
                errorMessage += `\n• ${fieldName}: ${Array.isArray(messages) ? messages.join(', ') : messages}`;
            }
        } else {
            errorMessage += "\n• Неверные данные формы";
        }
    
        errorMessage += "\n\nПожалуйста, проверьте введенные данные и попробуйте снова.";
    
        alert(errorMessage);
    },

    handleServerError(responseBody) {
        let errorMessage = "⚠️ Внутренняя ошибка сервера.";
    
        if (responseBody && responseBody.error) {
            errorMessage += `\n${responseBody.error}`;
            if (responseBody.details) {
                errorMessage += `\nДетали: ${responseBody.details}`;
            }
        }
    
        errorMessage += "\n\nПожалуйста, попробуйте позже или свяжитесь с поддержкой.";
    
        alert(errorMessage);
    },

    handleUnknownError(response, responseBody) {
        console.error("Unknown error response:", response, responseBody);
    
        let errorMessage = `❌ Неизвестная ошибка (статус: ${response.status})`;
    
        if (responseBody && responseBody.error) {
            errorMessage += `: ${responseBody.error}`;
        }
    
        errorMessage += "\n\nПожалуйста, свяжитесь с поддержкой.";
    
        alert(errorMessage);
    },

    async validateDeliveryTime(date, time) {
        if (!date || !time) return { valid: false, reason: "Укажите дату и время доставки" };
    
        try {
            const response = await fetch(`${this.apiBaseAddress}/delivery/validate/`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json", 
                    Accept: "application/json" 
                },
                body: JSON.stringify({ date, time }),
            });
        
            if (response.ok) {
                return await response.json();
            }
        
            return this.clientSideTimeValidation(date, time);
        
        } catch (error) {
            console.error("Validation error:", error);
            return this.clientSideTimeValidation(date, time);
        }
    },

    clientSideTimeValidation(date, time) {
        try {
            const deliveryDateTime = new Date(`${date}T${time}`);
            const now = new Date();
            const minDeliveryTime = new Date(now.getTime() + 5 * 60 * 60 * 1000); // +5 часов
        
            if (deliveryDateTime < now) {
                return { valid: false, reason: "Время доставки не может быть в прошлом" };
            }
        
            if (deliveryDateTime < minDeliveryTime) {
                const minTimeStr = minDeliveryTime.toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                return { valid: false, reason: `Минимальное время заказа - через 5 часов. Ближайшее время: ${minTimeStr}` };
            }
        
            const deliveryHour = deliveryDateTime.getHours();
            if (deliveryHour < 10 || deliveryHour >= 23) {
                return { valid: false, reason: "Доставка возможна только с 10:00 до 23:00" };
            }
        
            return { valid: true };
        
        } catch (error) {
            return { valid: false, reason: "Неверный формат даты или времени" };
        }
    },

    getStatusText(status) {
        const statusMap = {
            'Заявка обрабатывается': '📋 Обрабатывается',
            'Готовим ваш торт': '👨‍🍳 В приготовлении',
            'Продукт в пути': '🚚 В доставке',
            'Продукт у вас': '✅ Доставлен'
        };
        return statusMap[status] || status;
    },

    getFieldName(field) {
        const fieldNames = {
            'DATE': '📅 Дата доставки',
            'TIME': '⏰ Время доставки',
            'NAME': '👤 Имя',
            'PHONE': '📞 Телефон',
            'EMAIL': '📧 Email',
            'ADDRESS': '🏠 Адрес',
            'LEVELS': '🎂 Количество уровней',
            'FORM': '🔷 Форма',
            'TOPPING': '🍯 Топпинг',
            'BERRIES': '🍓 Ягоды',
            'DECOR': '✨ Декор',
            'WORDS': '💬 Надпись',
            'gdpr': '📝 Согласие на обработку данных'
        };
        return fieldNames[field] || field;
    },

    resetOrderForm() {
        this.Levels = 0;
        this.Form = 0;
        this.Topping = 0;
        this.Berries = 0;
        this.Decor = 0;
        this.Words = "";
        this.Comments = "";
        this.Designed = false;
    
        this.Name = "";
        this.Phone = null;
        this.Email = null;
        this.Address = null;
        this.Dates = null;
        this.Time = null;
        this.DelivComments = "";
        this.GDPRConsent = false;
    
        window.scrollTo({ top: 0, behavior: 'smooth' });
    
        this.fetchCatalogOptions();
    
        console.log("Форма заказа сброшена");
    }
  }
}).mount("#VueApp");