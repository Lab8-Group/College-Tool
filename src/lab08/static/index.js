const BASE_URL = ""

// DOM Elements





/*function renderTable(data) {
    if (!data || Object.keys(data).length === 0) {
        displayArea.innerHTML = "<p>No records found.</p>";
        return;
    }

    let tableHtml = `
        <table class="grades-table">
            <thead>
                <tr>
                    <th>Student Name</th>
                    <th>Grade</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (const [name, grade] of Object.entries(data)) {
        tableHtml += `
            <tr>
                <td>${name}</td>
                <td>${grade}</td>
            </tr>
        `;
    }

    tableHtml += `</tbody></table>`;
    displayArea.innerHTML = tableHtml;
}
*/

async function getAllStudents() {
    

    try {
        const response = await fetch(BASE_URL);

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        
    } catch (error) {
        
    }
}


async function getStudent(studentName) {
    

    try {
        const response = await fetch(`${BASE_URL}/${encodeURIComponent(studentName)}`);

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
       
    } catch (error) {
        
    }
}


/* async function createStudent(studentName, gradeValue) {
    

    try {
        const response = await fetch(BASE_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: studentName,
                grade: gradeValue
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        
    } catch (error) {
       
    }
} */


async function editStudent(studentName, newGrade) {
    

    try {
        const response = await fetch(`${BASE_URL}/${encodeURIComponent(studentName)}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                grade: newGrade
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        
    } catch (error) {
        
    }
}


export async function unEnrollSelf(courseId) {
    
        const response = await fetch(`${BASE_URL}/courses/${courseId}/leaving`, {
            method: "DELETE",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}




