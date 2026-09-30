async function api(url, options = {}) {
  const opts = {...options, headers: {...(options.headers || {})}};
  if (opts.body && !(opts.body instanceof FormData)) {
    opts.headers["Content-Type"] = "application/json";
  }
  const response = await fetch(url, opts);
  let data = {};
  try { data = await response.json(); } catch {}
  if (response.status === 401) {
    if (!location.pathname.includes("/login") && !location.pathname.includes("/register")) {
      location.href = "/login";
    }
  }
  if (!response.ok && !data.message) {
    data.message = data.detail || "Request failed";
  }
  return data;
}

function money(n) {
  return "₹" + Number(n || 0).toLocaleString("en-IN", {maximumFractionDigits: 2});
}

async function renderPlanner(url, body, multipart=false) {
  const result = document.getElementById("result");
  result.innerHTML = '<section class="card loading">Generating your plan…</section>';
  const data = await api(url, {method:"POST", body});
  if (!data.title) {
    result.innerHTML = `<section class="card error">${data.message || "Could not generate the plan."}</section>`;
    return;
  }
  result.innerHTML = `
    <section class="card result-card">
      <div class="section-head"><div><span class="eyebrow">${data.source || "AI"}</span><h2>${data.title}</h2></div><strong>${money(data.total_estimated_cost)}</strong></div>
      <p>${data.summary}</p>
      <div class="budget-line"><span>Budget</span><b>${money(data.budget)}</b><span>Remaining</span><b>${money(data.budget_remaining)}</b></div>
      <h3>Budget allocation</h3>
      <div class="allocation-grid">${(data.allocations||[]).map(a=>`<div><b>${a.category}</b><span>${money(a.amount)}</span></div>`).join("")}</div>
      <h3>Recommendations</h3>
      <div class="grid three">${(data.recommendations||[]).map(i=>`
        <article class="recommendation">
          <span class="tag">${i.platform}</span>
          <h3>${i.name}</h3>
          <p>${i.reason}</p>
          <div><b>${money(i.estimated_price)}</b> × ${i.quantity}</div>
          <a class="btn small secondary" href="${i.search_url}" target="_blank" rel="noopener">Search platform</a>
        </article>`).join("")}</div>
      <h3>Notes</h3>
      <ul>${(data.notes||[]).map(n=>`<li>${n}</li>`).join("")}</ul>
    </section>`;
}
document.getElementById("logoutBtn")?.addEventListener("click", async()=>{
  document.cookie="access_token=; Max-Age=0; Path=/; SameSite=Lax";
  location.href="/";
});
