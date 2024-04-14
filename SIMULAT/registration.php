<?php
// Connect to the database
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "simulatdb";

$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to generate a random student ID with the current year
function generateStudentID() {
    $year = date("Y");
    $randomNumber = mt_rand(100000, 999999);
    return $year . $randomNumber;
}

// Function to generate a random token ID
function generateTokenID() {
    return 'TOKEN' . mt_rand(100000, 999999);
}

// Function to sanitize user input
function sanitizeInput($data) {
    return htmlspecialchars(stripslashes(trim($data)));
}

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Sanitize input data
    $givenName = sanitizeInput($_POST["given_name"]);
    $middleName = sanitizeInput($_POST["middle_name"]);
    $surname = sanitizeInput($_POST["surname"]);
    $dateOfBirth = sanitizeInput($_POST["date_of_birth"]);
    $gender = sanitizeInput($_POST["gender"]);
    $enrollmentDate = date("Y-m-d"); // Automatically set the enrollment date to the current date

    // Generate a random student ID and token ID
    $studentID = generateStudentID();
    $tokenID = generateTokenID();

    // Use prepared statement to insert the student information into the database
    $sql = "INSERT INTO Student (student_id, token_id, given_name, middle_name, surname, date_of_birth, gender, enrollment_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ssssssss", $studentID, $tokenID, $givenName, $middleName, $surname, $dateOfBirth, $gender, $enrollmentDate);

    if ($stmt->execute()) {
        echo "Student registration successful. Copy your Token ID: $tokenID";
        // You can redirect or display a link back to the login page here
        echo "<br><a href='login.php'>Go back to Login</a>";
    } else {
        echo "Error: " . $stmt->error;
    }

    // Close the statement
    $stmt->close();
}

// Close the database connection
$conn->close();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Registration</title>
</head>
<body>
    <h2>Student Registration</h2>
    <form method="post" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>">
        <table>
            <tr>
                <th>Given Name</th>
                <td><input type="text" name="given_name" required></td>
            </tr>
            <tr>
                <th>Middle Name</th>
                <td><input type="text" name="middle_name" required></td>
            </tr>
            <tr>
                <th>Surname</th>
                <td><input type="text" name="surname" required></td>
            </tr>
            <tr>
                <th>Date of Birth</th>
                <td><input type="date" name="date_of_birth" required></td>
            </tr>
            <tr>
                <th>Gender</th>
                <td>
                    <select name="gender" required>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </td>
            </tr>
            <!-- Enrollment Date will be automatically set to the current date -->
        </table>
        <br>
        <input type="submit" value="Register">
    </form>
</body>
</html>