document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("subject").addEventListener("change", function () {
        let subjectId = this.value;
        let topicDropdown = document.getElementById("topic");

        topicDropdown.innerHTML = '<option value="">Select a Topic</option>';

        if (subjectId) {
            fetch(`/get-topics/?subject_id=` + subjectId)
                .then(response => response.json())
                .then(data => {
                    data.forEach(topic => {
                        let option = document.createElement("option");
                        option.value = topic.id;
                        option.textContent = topic.name;
                        topicDropdown.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching topics:", error));
        }
    });
});
