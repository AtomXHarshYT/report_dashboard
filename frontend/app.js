const API = location.hostname === "localhost"
  ? "http://127.0.0.1:8000"
  : "https://report-dashboard-o8us.onrender.com";

const WS = location.hostname === "localhost"
  ? "ws://127.0.0.1:8000/ws"
  : "wss://report-dashboard-o8us.onrender.com/ws";
let socket;

let editId = null;
let allData = [];

window.onload = () => {
    const user = JSON.parse(localStorage.getItem("user"));
    document.getElementById("username").innerText =
        user.name + " (" + user.role + ")";

    connectWebSocket(); // 👈 ADD THIS
    loadTickets();
};

function clean(val) {
    return val.split(",").map(v => v.trim()).filter(v => v);
}

// LOAD
async function loadTickets() {
    const user = JSON.parse(localStorage.getItem("user"));

    const res = await fetch(`${API}/tickets/${user.id}/${user.role}`);
    const data = await res.json();

    allData = data;
    render(data);
}

// RENDER
function render(data) {
    const table = document.getElementById("table");
    table.innerHTML = "";

    data.forEach(t => {
        table.innerHTML += `
        <tr>
            <td>${t.date}</td>
            <td>${t.ticket_id || "-"}</td>
            <td>${(t.rest_ids || []).join(",")}</td>
            <td>${(t.vendor_ids || []).join(",")}</td>
            <td>${t.status}</td>
            <td>${(t.remarks || []).join(",")}</td>
            <td>
                <button onclick="edit('${t.id}', this)">Edit</button>
                <button onclick="del('${t.id}')">Delete</button>
            </td>
        </tr>
        `;
    });
}

function connectWebSocket() {
    socket = new WebSocket(WS);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
        console.log("Realtime:", event.data);

        if (event.data === "tickets_updated") {
            loadTickets();
        }
    };

    socket.onclose = () => {
        console.log("WebSocket disconnected... retrying");
        setTimeout(connectWebSocket, 2000); // auto reconnect
    };
}

// SAVE
async function saveTicket() {
    const user = JSON.parse(localStorage.getItem("user"));

    const body = {
        user_id: user.id,
        date: document.getElementById("date").value,
        ticket_id: document.getElementById("ticket_id").value || null,
        rest_ids: clean(document.getElementById("rest_ids").value),
        vendor_ids: clean(document.getElementById("vendor_ids").value),
        status: document.getElementById("status").value,
        remarks: clean(document.getElementById("remarks").value)
    };

    if (editId) {
        await fetch(`${API}/tickets/${editId}`, {
            method: "PUT",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(body)
        });
        editId = null;
    } else {
        await fetch(`${API}/tickets`, {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(body)
        });
    }

    document.getElementById("formDiv").style.display = "none";
    loadTickets();
}

// DELETE
async function del(id) {
    await fetch(`${API}/tickets/${id}`, { method:"DELETE" });
    loadTickets();
}

// EDIT
function edit(id, btn) {
    editId = id;
    const row = btn.closest("tr").children;

    document.getElementById("date").value = row[0].innerText;
    document.getElementById("ticket_id").value = row[1].innerText;
    document.getElementById("rest_ids").value = row[2].innerText;
    document.getElementById("vendor_ids").value = row[3].innerText;
    document.getElementById("status").value = row[4].innerText;
    document.getElementById("remarks").value = row[5].innerText;

    document.getElementById("formDiv").style.display = "block";
}

// FILTER
function applyFilter() {
    const val = document.getElementById("search").value.toLowerCase();

    const filtered = allData.filter(t =>
        (t.ticket_id || "").toLowerCase().includes(val)
    );

    render(filtered);
}

// OPEN FORM
function openForm() {
    document.getElementById("formDiv").style.display = "block";
}