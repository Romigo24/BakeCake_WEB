Vue.createApp({
    name: "App",
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            schema1: {
                lvls: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' количество уровней';
                },
                form: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' форму торта';
                },
                topping: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' топпинг';
                }
            },
            schema2: {
                name: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' имя';
                },
                phone: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' телефон';
                },
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-Я]+$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат имени нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                },
                phone_format:(value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                email: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' почту';
                },
                address: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' адрес';
                },
                date: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' дату доставки';
                },
                time: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' время доставки';
                }
            },
            DATA: {
                Levels: [],
                Forms: [],
                Toppings: [],
                Berries: [],
                Decors: []
                // Levels: ['не выбрано', '1', '2', '3'],
                // Forms: ['не выбрано', 'Круг', 'Квадрат', 'Прямоугольник'],
                // Toppings: ['не выбрано', 'Без', 'Белый соус', 'Карамельный', 'Кленовый', 'Черничный', 'Молочный шоколад', 'Клубничный'],
                // Berries: ['нет', 'Ежевика', 'Малина', 'Голубика', 'Клубника'],
                // Decors: [ 'нет', 'Фисташки', 'Безе', 'Фундук', 'Пекан', 'Маршмеллоу', 'Марципан']
            },
            Costs: {
                Levels: [],
                Forms: [],
                Toppings: [],
                Berries: [],
                Decors: [],
                Words: 500
                // Levels: [0, 400, 750, 1100],
                // Forms: [0, 600, 400, 1000],
                // Toppings: [0, 0, 200, 180, 200, 300, 350, 200],
                // Berries: [0, 400, 300, 450, 500],
                // Decors: [0, 300, 400, 350, 300, 200, 280],
                // Words: 500
            },
            Levels: 0,
            Form: 0,
            Topping: 0,
            Berries: 0,
            Decor: 0,
            Words: '',
            Comments: '',
            Designed: false,
            PromoCode:'',
            promoValid: false,
            promoDiscount: 0,
            promoChecked:false,
            Name: '',
            Phone: null,
            Email: null,
            Address: null,
            Dates: null,
            Time: null,
            DelivComments: '',
            optionsData: null,
        }
    },
    created() {
        this.fetchOptions().catch(error => {
            console.error("Ошибка загрузки опций:", error);
        });
    },
    methods: {

            async register() {
                try {
                    const response = await fetch('/api/register/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({
                            username: this.username,
                            password: this.password,
                            email: this.email
                        })
                    });

                    if (response.ok) {
                        this.success = true;
                        this.error = '';
                    } else {
                        const data = await response.json();
                        this.error = data.error || 'Ошибка регистрации';
                    }
                } catch (error) {
                    this.error = 'Ошибка сети';
                }
        },

        async fetchOptions() {
            try {
                const response = await fetch('/api/options/');
                const data = await response.json();

                this.DATA.Levels = data.levels.map(item => item.name);
                this.DATA.Forms = data.forms.map(item => item.name);
                this.DATA.Toppings = data.toppings.map(item => item.name);
                this.DATA.Berries = data.berries.map(item => item.name);
                this.DATA.Decors = data.decors.map(item => item.name);

                this.Costs.Levels = data.levels.map(item => item.price);
                this.Costs.Forms = data.forms.map(item => item.price);
                this.Costs.Toppings = data.toppings.map(item => item.price);
                this.Costs.Berries = data.berries.map(item => item.price);
                this.Costs.Decors = data.decors.map(item => item.price);

                this.optionsData = data;
                this.$forceUpdate();
            } catch (error) {
                console.error("Ошибка загрузки опций:", error);
            }
        },
        async ToStep4() {
            this.promoChecked = false;

            if (this.PromoCode) {
                try {
                    const response = await fetch('/api/ordercake/validate_promo/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({ promo: this.PromoCode })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        this.promoChecked = true;

                        if (result.valid) {
                            this.promoValid = true;
                            this.promoDiscount = result.discount;
                        } else {
                            this.promoValid = false;
                            return;
                        }
                    } else {
                        this.promoChecked = true;
                        this.promoValid = false;
                        throw new Error('Ошибка проверки промокода');
                    }
                } catch (error) {
                    this.promoChecked = true;
                    this.promoValid = false;
                    console.error("Ошибка проверки промокода:", error);
                    return;
                }
            }

            this.Designed = true;
            setTimeout(() => this.$refs.ToStep4.click(), 0);
        },
        onsubmit() {
                // this.$refs.HiddenFormSubmit.click()

                const orderData = {
                    cake: {
                        level_id: this.Levels + 1,
                        form_id: this.Form + 1,
                        topping_id: this.Topping + 1,
                        berry_id: this.Berries + 1,
                        decor_id: this.Decor + 1,
                        words: this.Words,
                        comment: this.DelivComments,
                    },
                    name: this.Name,
                    phone: this.Phone,
                    email: this.Email,
                    address: this.Address,
                    delivery_date: this.Dates,
                    delivery_time: this.Time,
                    comments: this.Comments,
                    promo: this.PromoCode
                };

              fetch('/api/ordercake/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(orderData)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Успех:", data);
                this.$refs.HiddenFormSubmit.click();
                alert("Заказ создан успешно!");
            })
            .catch(error => {
                console.error("Ошибка:", error);
                alert("Ошибка при создании заказа");
            });

        },
        getCSRFToken() {
            const cookie = document.cookie.match(/csrftoken=([^;]+)/);
            return cookie ? cookie[1] : '';
        }
    },
 computed: {
    Cost() {
        if (!this.Costs.Levels.length) return 0;

        let baseCost = Number(this.Costs.Levels[this.Levels] || 0) +
                      Number(this.Costs.Forms[this.Form] || 0) +
                      Number(this.Costs.Toppings[this.Topping] || 0) +
                      Number(this.Costs.Berries[this.Berries] || 0) +
                      Number(this.Costs.Decors[this.Decor] || 0) +
                      Number(this.Words ? this.Costs.Words : 0);

        return this.promoValid ? Math.round(baseCost * (1 - this.promoDiscount / 100)) : baseCost;
    }
}
}).mount('#VueApp')