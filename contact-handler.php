<?php
/**
 * Contact Form Handler, v2.1
 * Linda Chirwa Attorneys
 *
 * Receives POST submissions, validates, sanitizes, and emails to the firm.
 * Returns JSON so the front-end can show success/error without a page reload.
 *
 * v2 additions: matter_type, opposing_party, incident_date, documents_available[],
 *               budget_range, referral, contact_pref, consent
 * All new fields are optional; the handler remains backward-compatible.
 */

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    header('Content-Type: application/json');
    echo json_encode(['success' => false, 'message' => 'Method not allowed.']);
    exit;
}

header('Content-Type: application/json');

// Configuration
$recipientEmail = 'admin@lindachirwaattorneys.co.za';
$ccEmail        = 'info@lindachirwaattorneys.co.za';
$subjectPrefix  = '[Website Enquiry]';
$honeypotField  = 'website_url';

// Honeypot check (spam filter)
if (!empty($_POST[$honeypotField])) {
    echo json_encode(['success' => true, 'message' => 'Thank you for your message.']);
    exit;
}

// Helpers. The email is plain text, so values are cleaned rather than HTML-encoded:
// tags are removed and control characters stripped (which also blocks header injection).
function clean_line($val, $max = 200) {
    $val = is_string($val) ? strip_tags($val) : '';
    $val = preg_replace('/[\x00-\x1F\x7F]+/', ' ', $val);
    return mb_substr(trim($val), 0, $max);
}
function post_str($key, $max = 200) {
    return clean_line($_POST[$key] ?? '', $max);
}

// Collect and sanitize fields
$name           = post_str('name', 120);
$email          = post_str('email', 254);
$phone          = post_str('phone', 40);
$service        = post_str('service');
$matter_type    = post_str('matter_type');
$office         = post_str('office');
$urgency        = post_str('urgency');
$incident_date  = post_str('incident_date', 40);
$opposing_party = post_str('opposing_party');
$budget_range   = post_str('budget_range');
$referral       = post_str('referral');
$contact_pref   = post_str('contact_pref');
$consent        = post_str('consent');

// Free text: keep line breaks, drop tags and other control characters, cap length.
$message = isset($_POST['message']) && is_string($_POST['message']) ? $_POST['message'] : '';
$message = strip_tags($message);
$message = preg_replace('/[^\P{C}\n\r\t]+/u', '', $message) ?? '';
$message = mb_substr(trim($message), 0, 8000);

// Multi-select: documents_available[]
$documents = [];
if (!empty($_POST['documents_available']) && is_array($_POST['documents_available'])) {
    foreach (array_slice($_POST['documents_available'], 0, 20) as $doc) {
        $clean = clean_line($doc, 100);
        if ($clean !== '') $documents[] = $clean;
    }
}

// Validation
$errors = [];

if ($name === '') {
    $errors[] = 'Full name is required.';
}
if ($email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'A valid email address is required.';
}
if ($phone === '') {
    $errors[] = 'Phone number is required.';
}
if ($service === '') {
    $errors[] = 'Please select an area of law.';
}
if ($message === '') {
    $errors[] = 'Please describe your legal matter.';
}
if ($consent !== 'yes') {
    $errors[] = 'Please confirm your consent to be contacted.';
}

if (!empty($errors)) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => implode(' ', $errors)]);
    exit;
}

// Build email
$subject = mb_encode_mimeheader($subjectPrefix . ' ' . $name . ' | ' . ($service ?: 'General Enquiry'), 'UTF-8', 'B', "\r\n");

$line = str_repeat('-', 48);

$body  = "NEW WEBSITE ENQUIRY\n";
$body .= str_repeat('=', 48) . "\n\n";

$body .= "CONTACT DETAILS\n";
$body .= $line . "\n";
$body .= "Name:          {$name}\n";
$body .= "Email:         {$email}\n";
$body .= "Phone:         {$phone}\n";
$body .= "Preferred:     " . ($contact_pref ?: 'No preference') . "\n\n";

$body .= "MATTER DETAILS\n";
$body .= $line . "\n";
$body .= "Area of law:   " . ($service ?: 'Not specified') . "\n";
$body .= "Enquirer is:   " . ($matter_type ?: 'Not specified') . "\n";
$body .= "Office:        " . ($office ?: 'Not specified') . "\n";
$body .= "Urgency:       " . ($urgency ?: 'Not specified') . "\n";
$body .= "Incident date: " . ($incident_date ?: 'Not specified') . "\n";
$body .= "Opposing party:" . ($opposing_party ? ' ' . $opposing_party : ' Not specified') . "\n";
$body .= "Budget range:  " . ($budget_range ?: 'Not specified') . "\n";
$body .= "Referral:      " . ($referral ?: 'Not specified') . "\n";
$body .= "Documents:     " . (!empty($documents) ? implode(', ', $documents) : 'None selected') . "\n\n";

$body .= "MESSAGE\n";
$body .= $line . "\n";
$body .= $message . "\n\n";

$body .= $line . "\n";
$body .= "Submitted: " . date('Y-m-d H:i:s') . " (server time)\n";
$body .= "IP:        " . ($_SERVER['REMOTE_ADDR'] ?? 'unknown') . "\n";
$body .= "UA:        " . ($_SERVER['HTTP_USER_AGENT'] ?? 'unknown') . "\n";

$headers  = "From: website@lindachirwaattorneys.co.za\r\n";
$headers .= "Reply-To: {$email}\r\n";
$headers .= "Cc: {$ccEmail}\r\n";
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "Content-Transfer-Encoding: 8bit\r\n";
$headers .= "X-Mailer: LindaChirwaContactForm/2.1";

// Send
$sent = @mail($recipientEmail, $subject, $body, rtrim($headers));

if ($sent) {
    echo json_encode([
        'success' => true,
        'message' => 'Thank you, ' . $name . '. Your enquiry has been received. We will be in touch within 24 hours.'
    ]);
} else {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => 'We could not send your message at this time. Please call us on +27 (10) 085 5185 or email admin@lindachirwaattorneys.co.za.'
    ]);
}