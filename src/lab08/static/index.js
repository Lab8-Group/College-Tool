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




export async function Login(name, password) {
    
        const response = await fetch(`${BASE_URL}/login`, {
            method: "POST",
            credentials: "include",
            headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}

export async function logOut() {
    
        const response = await fetch(`${BASE_URL}/logout`, {
            method: "POST",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}

export async function getUser() {
    
        const response = await fetch(`${BASE_URL}/me`, {
            method: "GET",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}


export async function allCourses() {
    
        const response = await fetch(`${BASE_URL}/courses`, {
            method: "GET",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}

export async function yourCourses() {
    
        const response = await fetch(`${BASE_URL}/my-courses`, {
            method: "GET",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;


}

export async function EnrollSelf(courseId) {
    
        const response = await fetch(`${BASE_URL}/courses/${courseId}/enrollment`, {
            method: "PUT",
            credentials:"include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}


export async function getCourseStudents(courseId) {
    
        const response = await fetch(`${BASE_URL}/grades/${courseId}/students`, {
            method: "GET",
            credentials: "include"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}



export async function editStudent(courseId, studentId, newGrade) {
    
        const response = await fetch(`${BASE_URL}/grades/${courseId}/students/${studentId}/grade`, {
            method: "PUT",
            credentials:" include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                grade: newGrade
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP Error: ${response.status}`);
        }
        
     
    return data;
}