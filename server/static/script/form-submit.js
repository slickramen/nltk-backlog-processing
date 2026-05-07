function setDisplay(id, value) {
	const el = document.getElementById(id);
	if (value) {
		el.textContent = value;
		el.classList.remove("empty");
	} else {
		el.textContent = "—";
		el.classList.add("empty");
	}
}

document.addEventListener("DOMContentLoaded", function () {
	const empty = document.querySelector("#output-empty-state");
	const outputData = document.querySelector("#output-data");

	document.querySelector("#clear-btn").addEventListener("click", function () {
		document.querySelectorAll("input, select, textarea").forEach((el) => {
			if (el.type === "checkbox" || el.type === "radio") {
				el.checked = false;
			} else {
				el.value = "";
			}
		});

		empty.classList.add("show");
		outputData.classList.add("hide");
	});

	document
		.querySelector("#submit-btn")
		.addEventListener("click", function (e) {
			e.preventDefault();
			const form = document.getElementById("task-form");
			if (!form) {
				console.error("Form not found");
				return;
			}
			const data = Object.fromEntries(new FormData(form).entries());

			// Validation
			if (data.title.length === 0) {
				return;
			}

			fetch("/recommender/v1/categorise-task", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify(data),
			})
				.then((res) => res.json())
				.then((response) => {
					console.log(response);

					empty.classList.remove("show");
					outputData.classList.remove("hide");

					setDisplay("display-title", response.received.title);
					setDisplay(
						"display-description",
						response.received.description,
					);
					setDisplay(
						"display-techstack",
						response.received.stack_layer,
					);
					setDisplay(
						"display-stack-source",
						response.received.stack_source,
					);

					// Reset and display concepts
					const conceptContainer =
						document.querySelector("#display-concepts");
					conceptContainer.innerHTML = "";

					document.querySelector("#display-concept-count").innerHTML =
						response.received.core_concepts.length;

					response.received.core_concepts.forEach((tag) => {
						const tagDiv = document.createElement("div");
						tagDiv.textContent = tag;
						tagDiv.classList.add("tag");
						conceptContainer.appendChild(tagDiv);
					});

					// Reset and display impls
					const implContainer = document.querySelector(
						"#display-implementations",
					);
					implContainer.innerHTML = "";

					document.querySelector(
						"#display-implementation-count",
					).innerHTML = response.received.implementation_types.length;

					response.received.implementation_types.forEach((tag) => {
						const tagDiv = document.createElement("div");
						tagDiv.textContent = tag;
						tagDiv.classList.add("tag");
						implContainer.appendChild(tagDiv);
					});

					// Reset and display tokens
					const tokenContainer =
						document.querySelector("#display-tokens");
					tokenContainer.innerHTML = "";

					document.querySelector("#display-token-count").innerHTML =
						response.received.tokens_used.length;

					response.received.tokens_used.forEach((tag) => {
						const tagDiv = document.createElement("div");
						tagDiv.textContent = tag;
						tagDiv.classList.add("tag");
						tokenContainer.appendChild(tagDiv);
					});
				})
				.catch((err) => {
					console.error("Error:", err);
				});
		});
});
