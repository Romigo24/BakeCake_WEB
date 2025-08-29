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

      const response = await fetch(`${this.apiBaseAddress}/orders/create/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(this.buildOrderPayload()),
      });

      let responseBody = {};
      try { responseBody = await response.json(); } catch {}

      this.orderSubmittingInProgress = false;

      if (response.status === 201 && responseBody && responseBody.order_id) {
        alert("Заказ оформлен, №" + responseBody.order_id);
      } else if (response.status === 409 && responseBody && typeof responseBody.server_total === "number") {
        alert("Цена изменилась. Сервер: " + responseBody.server_total + "₽");
      } else {
        alert("Ошибка при оформлении заказа");
      }
    },
  },
}).mount("#VueApp");
