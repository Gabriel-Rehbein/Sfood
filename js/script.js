const API_BASE = "http://127.0.0.1:5000";

/* ELEMENTOS GLOBAIS */

const navButtons = document.querySelectorAll(".nav-btn");
const views = document.querySelectorAll(".view-area");

const produtosListEl = document.getElementById("produtos-list");
const carrinhoListEl = document.getElementById("carrinho-list");
const recomendacoesListEl = document.getElementById("recomendacoes-list");
const btnRecarregarProdutos = document.getElementById("btn-recarregar-produtos");
const btnRecomendacoes = document.getElementById("btn-recomendacoes");

const chatMessagesEl = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

const plannerForm = document.getElementById("planner-form");
const plannerResultEl = document.getElementById("planner-result");

const btnRecarregarPedidos = document.getElementById("btn-recarregar-pedidos");
const intranetBodyEl = document.getElementById("intranet-pedidos-body");

const btnRecarregarAnalytics = document.getElementById("btn-recarregar-analytics");

// IDs que EXISTEM no HTML do CEO:
const kpiTotalProdutos = document.getElementById("kpi-total-produtos");
const kpiTotalPedidos = document.getElementById("kpi-total-pedidos");
const kpiTotalClientes = document.getElementById("kpi-total-clientes");
const ceoResumoTexto = document.getElementById("ceo-resumo-texto");

// Gráfico CEO
const btnRecarregarGrafico = document.getElementById("btn-recarregar-grafico");
const chartCanvas = document.getElementById("chart-vendas-categorias");
let chartVendasCategorias = null;

let carrinho = [];

/* NAV */

navButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.target;

    navButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    views.forEach((v) => {
      if (v.id === target) {
        v.classList.add("active");
        v.classList.add("fade-in");
      } else {
        v.classList.remove("active");
      }
    });
  });
});

/* HELPERS FETCH */

async function apiGet(path) {
  const res = await fetch(API_BASE + path);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  if (!res.ok) throw new Error(`POST ${path} -> ${res.status}`);
  return res.json();
}

/* CLIENTE — PRODUTOS */

async function carregarProdutos() {
  if (!produtosListEl) return;

  produtosListEl.innerHTML = `<p class="placeholder">Carregando produtos...</p>`;
  try {
    const produtos = await apiGet("/api/cliente/produtos");
    if (!produtos || produtos.length === 0) {
      produtosListEl.innerHTML = `<p class="placeholder">Nenhum produto cadastrado no sistema.</p>`;
      return;
    }

    produtosListEl.innerHTML = "";
    produtos.forEach((prod) => {
      const item = document.createElement("div");
      item.className = "produto-item";

      const info = document.createElement("div");
      info.className = "produto-info";

      const nome = document.createElement("div");
      nome.className = "produto-nome";
      nome.textContent = prod.nome;

      const desc = document.createElement("div");
      desc.className = "produto-desc";
      desc.textContent = prod.descricao || "";

      const tags = document.createElement("div");
      tags.className = "produto-tags";
      tags.textContent = prod.tags_texto || "";

      info.appendChild(nome);
      info.appendChild(desc);
      info.appendChild(tags);

      const meta = document.createElement("div");
      meta.className = "produto-meta";

      const preco = document.createElement("div");
      preco.className = "produto-preco";
      if (prod.preco != null) {
        preco.textContent = `R$ ${Number(prod.preco)
          .toFixed(2)
          .replace(".", ",")}`;
      } else {
        preco.textContent = "R$ --";
      }

      const btnAdd = document.createElement("button");
      btnAdd.className = "btn ghost";
      btnAdd.textContent = "Adicionar";
      btnAdd.addEventListener("click", () => {
        adicionarAoCarrinho(prod);
      });

      meta.appendChild(preco);

      if (prod.eh_saudavel) {
        const tagSaude = document.createElement("span");
        tagSaude.className = "tag-saude";
        tagSaude.textContent = "Saudável";
        meta.appendChild(tagSaude);
      }

      meta.appendChild(btnAdd);

      item.appendChild(info);
      item.appendChild(meta);
      produtosListEl.appendChild(item);
    });
  } catch (err) {
    console.error(err);
    produtosListEl.innerHTML = `<p class="placeholder">Erro ao carregar produtos.</p>`;
  }
}

function atualizarCarrinhoView() {
  if (!carrinhoListEl) return;

  if (!carrinho.length) {
    carrinhoListEl.innerHTML = `<p class="placeholder">Nenhum item no carrinho ainda.</p>`;
    return;
  }

  carrinhoListEl.innerHTML = "";
  carrinho.forEach((item, idx) => {
    const row = document.createElement("div");
    row.className = "carrinho-item";

    const nome = document.createElement("span");
    nome.textContent = item.nome;

    const actions = document.createElement("div");
    const btnRemove = document.createElement("button");
    btnRemove.className = "btn ghost";
    btnRemove.textContent = "Remover";
    btnRemove.style.padding = "0.2rem 0.6rem";
    btnRemove.addEventListener("click", () => {
      carrinho.splice(idx, 1);
      atualizarCarrinhoView();
    });

    actions.appendChild(btnRemove);
    row.appendChild(nome);
    row.appendChild(actions);
    carrinhoListEl.appendChild(row);
  });
}

function adicionarAoCarrinho(prod) {
  carrinho.push({ id: prod.id, nome: prod.nome });
  atualizarCarrinhoView();
}

/* CLIENTE — RECOMENDAÇÕES */

async function carregarRecomendacoes() {
  if (!recomendacoesListEl) return;

  if (!carrinho.length) {
    recomendacoesListEl.innerHTML = `<p class="placeholder">Adicione pelo menos um item ao carrinho para ver recomendações.</p>`;
    return;
  }

  const ids = carrinho.map((p) => p.id);
  recomendacoesListEl.innerHTML = `<p class="placeholder">Consultando IA de recomendações...</p>`;

  try {
    const recs = await apiPost("/api/cliente/recomendacoes", { ids });
    if (!recs || !recs.length) {
      recomendacoesListEl.innerHTML = `<p class="placeholder">Nenhuma recomendação encontrada.</p>`;
      return;
    }

    recomendacoesListEl.innerHTML = "";
    recs.forEach((r) => {
      const row = document.createElement("div");
      row.className = "recomendacao-item";

      const info = document.createElement("div");
      info.innerHTML = `<strong>${r.nome}</strong><br><span class="produto-tags">${
        r.categoria || ""
      }</span>`;

      const score = document.createElement("span");
      score.className = "badge-score";
      const s = r.score != null ? r.score : 0;
      score.textContent = `score: ${(s * 100).toFixed(0)}%`;

      row.appendChild(info);
      row.appendChild(score);
      recomendacoesListEl.appendChild(row);
    });
  } catch (err) {
    console.error(err);
    recomendacoesListEl.innerHTML = `<p class="placeholder">Erro ao consultar recomendações.</p>`;
  }
}

/* CHATBOT */

function adicionarMensagem(tipo, texto) {
  if (!chatMessagesEl) return;

  const msg = document.createElement("div");
  msg.className = `chat-message ${tipo}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = texto;
  msg.appendChild(bubble);
  chatMessagesEl.appendChild(msg);
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

chatForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const pergunta = chatInput.value.trim();
  if (!pergunta) return;

  adicionarMensagem("user", pergunta);
  chatInput.value = "";
  adicionarMensagem("bot", "Pensando...");

  try {
    const res = await apiPost("/api/ia/chat", { pergunta });
    const lastPlaceholder = chatMessagesEl.querySelector(
      ".chat-message.bot:last-child .bubble"
    );
    if (lastPlaceholder && lastPlaceholder.textContent === "Pensando...") {
      lastPlaceholder.textContent =
        res.resposta || "Não entendi sua pergunta.";
    } else {
      adicionarMensagem("bot", res.resposta || "Não entendi sua pergunta.");
    }
  } catch (err) {
    console.error(err);
    adicionarMensagem(
      "bot",
      "Tive um erro ao buscar a resposta, tente novamente."
    );
  }
});

/* PLANNER */

plannerForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const diasInput = document.getElementById("planner-dias");
  const dias = parseInt(diasInput.value || "7", 10);

  const prefs = [];
  plannerForm
    .querySelectorAll('input[type="checkbox"]:checked')
    .forEach((chk) => {
      prefs.push(chk.value);
    });

  plannerResultEl.innerHTML = `<p class="placeholder">Gerando plano de refeições...</p>`;

  try {
    const res = await apiPost("/api/ia/planner-refeicoes", {
      dias,
      preferencias: prefs,
    });

    if (!res || !res.dias || !res.dias.length) {
      plannerResultEl.innerHTML = `<p class="placeholder">Não foi possível montar o plano.</p>`;
      return;
    }

    plannerResultEl.innerHTML = "";
    res.dias.forEach((dia) => {
      const diaEl = document.createElement("div");
      diaEl.className = "planner-dia";
      const h3 = document.createElement("h3");
      h3.textContent = `Dia ${dia.dia}`;
      diaEl.appendChild(h3);

      (dia.refeicoes || []).forEach((ref, idx) => {
        const refEl = document.createElement("div");
        refEl.className = "planner-refeicao";
        const label =
          idx === 0 ? "Café da manhã" : idx === 1 ? "Almoço" : "Jantar";
        refEl.textContent = `${label}: ${ref.nome}`;
        diaEl.appendChild(refEl);
      });

      plannerResultEl.appendChild(diaEl);
    });
  } catch (err) {
    console.error(err);
    plannerResultEl.innerHTML = `<p class="placeholder">Erro ao gerar plano.</p>`;
  }
});

/* INTRANET */

async function carregarPedidos() {
  if (!intranetBodyEl) return;

  intranetBodyEl.innerHTML = `
    <tr><td colspan="5" class="placeholder-cell">Carregando pedidos...</td></tr>
  `;
  try {
    const pedidos = await apiGet("/api/intranet/pedidos");
    if (!pedidos || !pedidos.length) {
      intranetBodyEl.innerHTML = `
        <tr><td colspan="5" class="placeholder-cell">Nenhum pedido encontrado.</td></tr>
      `;
      return;
    }

    intranetBodyEl.innerHTML = "";
    pedidos.forEach((p) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td>${p.cliente_nome || "-"}</td>
        <td>R$ ${Number(p.total || 0).toFixed(2).replace(".", ",")}</td>
        <td>${p.status || "-"}</td>
        <td>${p.criado_em || "-"}</td>
      `;
      intranetBodyEl.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    intranetBodyEl.innerHTML = `
      <tr><td colspan="5" class="placeholder-cell">Erro ao carregar pedidos.</td></tr>
    `;
  }
}

/* CEO — KPIs + RESUMO */

async function carregarAnalytics() {
  if (!ceoResumoTexto) return;

  ceoResumoTexto.textContent = "Carregando dados...";
  try {
    const data = await apiGet("/api/ceo/analytics");
    const info = data || {};

    if (kpiTotalProdutos)
      kpiTotalProdutos.textContent = info.total_produtos ?? "0";
    if (kpiTotalPedidos)
      kpiTotalPedidos.textContent = info.total_pedidos ?? "0";
    if (kpiTotalClientes)
      kpiTotalClientes.textContent = info.total_clientes ?? "0";

    ceoResumoTexto.innerHTML = `
      Atualmente temos <strong>${info.total_produtos ?? 0}</strong> produtos ativos,
      <strong>${info.total_pedidos ?? 0}</strong> pedidos registrados
      e <strong>${info.total_clientes ?? 0}</strong> clientes na base.
    `;
  } catch (err) {
    console.error(err);
    ceoResumoTexto.textContent = "Erro ao carregar dados.";
  }
}

/* CEO — GRÁFICO VENDAS POR CATEGORIA */

async function carregarGraficoVendas() {
  if (!chartCanvas) return;

  try {
    const data = await apiGet("/api/ceo/vendas-categorias");
    if (!data || !data.labels || !data.series) {
      console.warn("Dados inválidos para gráfico de vendas", data);
      return;
    }

    const labels = data.labels;
    const series = data.series;

    const datasets = series.map((serie) => ({
      label: serie.label,
      data: serie.data,
      fill: false,
      tension: 0.25,
    }));

    if (chartVendasCategorias) {
      chartVendasCategorias.data.labels = labels;
      chartVendasCategorias.data.datasets = datasets;
      chartVendasCategorias.update();
      return;
    }

    const ctx = chartCanvas.getContext("2d");
    chartVendasCategorias = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        stacked: false,
        plugins: {
          legend: {
            position: "bottom",
          },
          tooltip: {
            callbacks: {
              label: (context) => {
                const v = context.parsed.y || 0;
                return `${context.dataset.label}: R$ ${v
                  .toFixed(2)
                  .replace(".", ",")}`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => `R$ ${value}`,
            },
          },
        },
      },
    });
  } catch (err) {
    console.error("Erro ao carregar gráfico de vendas", err);
  }
}

/* BOTÕES RECARREGAR */

btnRecarregarProdutos?.addEventListener("click", carregarProdutos);
btnRecomendacoes?.addEventListener("click", carregarRecomendacoes);
btnRecarregarPedidos?.addEventListener("click", carregarPedidos);
btnRecarregarAnalytics?.addEventListener("click", carregarAnalytics);
btnRecarregarGrafico?.addEventListener("click", carregarGraficoVendas);

/* INICIALIZAÇÃO */

carregarProdutos();
carregarAnalytics();
carregarGraficoVendas();
carregarPedidos();
