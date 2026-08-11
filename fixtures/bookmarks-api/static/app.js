async function loadBookmarks() {
  const res = await fetch("/bookmarks");
  const bookmarks = await res.json();
  const list = document.getElementById("bookmark-list");
  list.innerHTML = "";
  for (const b of bookmarks) {
    const li = document.createElement("li");
    li.innerHTML = `<a href="${b.url}" target="_blank">${b.title}</a>`;
    list.appendChild(li);
  }
}

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = document.getElementById("url").value;
  const title = document.getElementById("title").value;
  await fetch("/bookmarks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, title }),
  });
  e.target.reset();
  loadBookmarks();
});

loadBookmarks();
