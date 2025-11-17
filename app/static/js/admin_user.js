// app/static/js/admin_user.js
// --- API BASE URL ---
const API_URL = '/api/users'; 

// --- FIX: Added Majors Data ---
const majorsData = {
  "คณะนิติศาสตร์": [
    "นิติศาสตรบัณฑิต (ท่าพระจันทร์)",
    "นิติศาสตรบัณฑิต (ศูนย์รังสิต)",
    "นิติศาสตรบัณฑิต (ศูนย์ลำปาง)",
    "นิติศาสตรบัณฑิต สาขาวิชากฎหมายธุรกิจ (นานาชาติ)"
  ],
  "คณะพาณิชยศาสตร์และการบัญชี": [
    "บัญชีบัณฑิต",
    "บัญชีบัณฑิต (นานาชาติ)",
    "บริหารธุรกิจบัณฑิต วิชาเอกการเงิน",
    "บริหารธุรกิจบัณฑิต วิชาเอกการตลาด",
    "บริหารธุรกิจบัณฑิต วิชาเอกการบริหารองค์การการประกอบการและทรัพยากรมนุษย์",
    "บริหารธุรกิจบัณฑิต วิชาเอกบริหารการปฏิบัติการ",
    "บริหารธุรกิจบัณฑิต วิชาเอกบริหารธุรกิจระหว่างประเทศ โลจิสติกส์และการขนส่ง",
    "บริหารธุรกิจบัณฑิต วิชาเอกระบบสารสนเทศเพื่อการจัดการ",
    "บริหารธุรกิจบัณฑิต วิชาเอกธุรกิจอสังหาริมทรัพย์",
    "บริหารธุรกิจบัณฑิต วิชาเอกการเงิน (นานาชาติ)",
    "บริหารธุรกิจบัณฑิต วิชาเอกการตลาด (นานาชาติ)",
    "ควบบัญชีบัณฑิต สาขาวิชาการบัญชีธุรกิจแบบบูรณาการ",
    "ควบบริหารธุรกิจบัณฑิต  สาขาวิชาการจัดการธุรกิจแบบบูรณาการ (นานาชาติ)"
  ],
  "คณะรัฐศาสตร์": [
    "รัฐศาสตรบัณฑิต วิชาเอกการเมืองการปกครอง",
    "รัฐศาสตรบัณฑิต วิชาเอกบริหารรัฐกิจ",
    "รัฐศาสตรบัณฑิต วิชาเอกการระหว่างประเทศ",
    "รัฐศาสตรบัณฑิต สาขาวิชาการเมืองและการระหว่างประเทศ (นานาชาติ)"
  ],
  "คณะเศรษฐศาสตร์": [
    "เศรษฐศาสตรบัณฑิต",
    "เศรษฐศาสตรบัณฑิต (นานาชาติ)"
  ],
  "คณะสังคมสงเคราะห์ศาสตร์": [
    "สังคมสงเคราะห์ศาสตรบัณฑิต (ศูนย์รังสิต)",
    "สังคมสงเคราะห์ศาสตรบัณฑิต (ศูนย์ลำปาง)",
    "ศิลปศาสตรบัณฑิต สาขาวิชานโยบายสังคมและการพัฒนา (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชานโยบายสังคมและการพัฒนา"
  ],
  "คณะวารสารศาสตร์และสื่อสารมวลชน": [
    "วารสารศาสตรบัณฑิต",
    "วารสารศาสตรบัณฑิต สาขาวิชาสื่อศึกษา (นานาชาติ)"
  ],
  "คณะสังคมวิทยาและมานุษยวิทยา": [
    "สังคมวิทยาและมานุษยวิทยาบัณฑิต สาขาวิชาสังคมวิทยาและมานุษยวิทยา",
    "สังคมวิทยาและมานุษยวิทยาบัณฑิต สาขาวิชาการวิจัยทางสังคม"
  ],
  "วิทยาลัยพัฒนศาสตร์ป๋วย อึ๊งภากรณ์": [
    "ศิลปศาสตรบัณฑิต สาขาวิชานวัตกรรมการพัฒนามนุษย์และสังคม"
  ],
  "วิทยาลัยนวัตกรรม": [
    "ศิลปศาสตรบัณฑิต สาขาวิชานวัตกรรมการบริการ (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาการจัดการมรดกวัฒนธรรมและอุตสาหกรรมสร้างสรรค์",
    "วิทยาศาสตรบัณฑิต สาขาวิชานวัตกรรมและการแปรรูปทางดิจิทัล"
  ],
  "วิทยาลัยสหวิทยาการ": [
    "ศิลปศาสตรบัณฑิต สาขาวิชาสหวิทยาการ (ศูนย์ลำปาง)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาปรัชญาการเมือง และเศรษฐศาสตร์ (ท่าพระจันทร์)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาปรัชญาการเมือง และเศรษฐศาสตร์ (ศูนย์ลำปาง)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์ และนวัตกรรมข้อมูล",
    "ศิลปศาสตรบัณฑิต สาขาวิชา ปรัชญา การเมือง และเศรษฐศาสตร์ (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาสหวิทยาการ (ศูนย์รังสิต)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาการจัดการ เพื่อความยั่งยืน"
  ],
  "วิทยาลัยนานาชาติปรีดีพนมยงค์": [
    "ศิลปศาสตรบัณฑิต สาขาวิชาจีนศึกษา (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาไทยศึกษา (นานาชาติ)"
  ],
  "คณะวิทยาการเรียนรู้และศึกษาศาสตร์": [
    "ศิลปศาสตรบัณฑิต สาขาวิชาวิทยาการเรียนรู้",
    "ศิลปศาสตรบัณฑิต สาขาวิชาศักยภาพ มนุษย์และสุขภาวะ"
  ],
  "วิทยาลัยโลกคดีศึกษา": [
    "ศิลปศาสตรบัณฑิต สาขาวิชาโลกคดีศึกษาและการประกอบการสังคม (นานาชาติ)"
  ],
  "คณะศิลปศาสตร์": [
    "วิทยาศาสตรบัณฑิต สาขาวิชาจิตวิทยา",
    "ศิลปศาสตรบัณฑิต วิชาเอกบรรณารักษศาสตร์และสารสนเทศศาสตร์",
    "ศิลปศาสตรบัณฑิต วิชาเอกประวัติศาสตร์",
    "ศิลปศาสตรบัณฑิต วิชาเอกปรัชญา",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาศาสตร์",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาและวรรณคดีอังกฤษ",
    "ศิลปศาสตรบัณฑิต วิชาเอกสเปนและลาตินอเมริกันศึกษา",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาฝรั่งเศส",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาเยอรมัน",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษารัสเซีย",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาและวัฒนธรรมจีน",
    "ศิลปศาสตรบัณฑิต วิชาเอกภาษาญี่ปุ่น",
    "ศิลปศาสตรบัณฑิต สาขาวิชาภาษาอังกฤษ",
    "ศิลปศาสตรบัณฑิต สาขาวิชาภาษาไทย",
    "วิทยาศาสตรบัณฑิต สาขาวิชาภูมิศาสตร์และภูมิสารสนเทศ",
    "ศิลปศาสตรบัณฑิต สาขาวิชาอาณาบริเวณศึกษา วิชาเอกเอเชียตะวันออกเฉียงใต้ศึกษา",
    "ศิลปศาสตรบัณฑิต สาขาวิชาอาณาบริเวณศึกษา วิชาเอกรัสเซียและยูเรเชียศึกษา",
    "ศิลปศาสตรบัณฑิต สาขาวิชาอาณาบริเวณศึกษา วิชาเอกเกาหลีศึกษา",
    "ศิลปศาสตรบัณฑิต สาขาวิชาอังกฤษ-อเมริกันศึกษา (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาการสื่อสาร เชิงธุรกิจ (นานาชาติ)",
    "ศิลปศาสตรบัณฑิต สาขาวิชาการแปล และล่ามในยุคดิจิทัล"
  ],
  "คณะศิลปกรรมศาสตร์": [
    "ศิลปกรรมศาสตรบัณฑิต สาขาวิชาการละคอน",
    "ศิลปกรรมศาสตรบัณฑิต สาขาวิชาศิลปะการออกแบบพัสตราภรณ์",
    "ศิลปกรรมศาสตรบัณฑิต สาขาวิชาออกแบบหัตถอุตสาหกรรม",
    "ศิลปกรรมศาสตรบัณฑิต สาขาวิชาการบริหารจัดการศิลปะ",
    "ศิลปกรรมศาสตรบัณฑิต สาขาวิชา ออกแบบหัตถอุตสาหกรรมสร้างสรรค์"
  ],
  "คณะวิทยาศาสตร์และเทคโนโลยี": [
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์สิ่งแวดล้อม",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีเพื่อการพัฒนายั่งยืน",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีการเกษตร",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการคอมพิวเตอร์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาคณิตศาสตร์ประยุกต์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาคณิตศาสตร์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาสถิติ",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และเทคโนโลยีการอาหาร",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเคมี",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีชีวภาพ",
    "วิทยาศาสตรบัณฑิต สาขาวิชาฟิสิกส์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาฟิสิกส์ อิเล็กทรอนิกส์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวัสดุศาสตร์",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และเทคโนโลยีสิ่งทอ",
    "วิทยาศาสตรบัณฑิต สาขาวิชาคณิตศาสตร์การจัดการ",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาการประกันภัย",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีพลังงานชีวภาพและการแปรรูปเคมีชีวภาพ",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์และนวัตกรรมทางอาหาร",
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีและนวัตกรรมดิจิทัล",
    "วิทยาศาสตรบัณฑิต สาขาวิชาคอมพิวเตอร์เครือข่ายและความปลอดภัยทางไซเบอร์"
  ],
  "คณะวิศวกรรมศาสตร์": [
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมไฟฟ้า",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมอุตสาหการ",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมโยธา",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเคมี",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเครื่องกล",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมซอฟต์แวร์",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมโยธาและการบริหารการก่อสร้าง",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมไฟฟ้าและการจัดการอุตสาหกรรม",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมยานยนต์และระบบอัตโนมัติ",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมไฟฟ้าและข้อมูล (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมโยธาและการพัฒนาอสังหาริมทรัพย์ (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเคมีและการจัดการ (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเครื่องกลและการจัดการอุตสาหกรรม (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมไฟฟ้า (นานาชาติ) (สองสถาบัน)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมโยธา (นานาชาติ) (สองสถาบัน)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเคมี (นานาชาติ) (สองสถาบัน)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเครื่องกล (นานาชาติ) (สองสถาบัน)"
  ],
  "คณะสถาปัตยกรรมศาสตร์และการผังเมือง": [
    "วิทยาศาสตรบัณฑิต สาขาวิชาสถาปัตยกรรม",
    "วิทยาศาสตรบัณฑิต สาขาวิชาสถาปัตยกรรมเพื่อการพัฒนาอสังหาริมทรัพย์",
    "การผังเมืองบัณฑิต",
    "ภูมิสถาปัตยกรรมศาสตรบัณฑิต",
    "สถาปัตยกรรมภายในบัณฑิต",
    "วิทยาศาสตรบัณฑิต สาขาวิชาการจัดการออกแบบธุรกิจและเทคโนโลยี (นานาชาติ)"
  ],
  "สถาบันเทคโนโลยีนานาชาติสิรินธร (SIIT)": [
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมไฟฟ้า (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมอุตสาหการและโลจิสติกส์อัจฉริยะ (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมโยธา (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเครื่องกล (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมเคมี (นานาชาติ)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาการวิเคราะห์ธุรกิจและโซ่อุปทาน (นานาชาติ)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาการจัดการวิศวกรรม (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์ (นานาชาติ)",
    "วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมดิจิทัล (นานาชาติ)"
  ],
  "คณะแพทยศาสตร์": [
    "แพทยศาสตรบัณฑิต",
    "แพทยศาสตรบัณฑิต (ภาษาอังกฤษ)",
    "การแพทย์แผนไทยประยุกต์บัณฑิต (ศูนย์รังสิต)",
    "การแพทย์แผนไทยประยุกต์บัณฑิต (ศูนย์ลำปาง)"
  ],
  "คณะทันตแพทยศาสตร์": [
    "ทันตแพทยศาสตรบัณฑิต",
    "ทันตแพทยศาสตรบัณฑิต (ทวิภาษา)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาทันตสาธารณสุข (ต่อเนื่อง)"
  ],
  "คณะสหเวชศาสตร์": [
    "เทคนิคการแพทยบัณฑิต",
    "วิทยาศาสตรบัณฑิต สาขาวิชากายภาพบำบัด",
    "วิทยาศาสตรบัณฑิต สาขาวิชาวิทยาศาสตร์การกีฬาและการออกกำลังกาย",
    "ศิลปศาสตรบัณฑิต สาขาวิชาการจัดการกีฬา",
    "ศิลปศาสตรบัณฑิต สาขาวิชาการฝึกสอนกีฬา",
    "วิทยาศาสตรบัณฑิต สาขาวิชารังสีเทคนิค"
  ],
    "คณะพยาบาลศาสตร์": [
    "พยาบาลศาสตรบัณฑิต"
  ],
  "คณะสาธารณสุขศาสตร์": [
    "วิทยาศาสตรบัณฑิต สาขาวิชาการสร้างเสริมสุขภาพเชิงนวัตกรรม",
    "วิทยาศาสตรบัณฑิต สาขาวิชาอาชีวอนามัยและความปลอดภัย (ศูนย์รังสิต)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาอาชีวอนามัยและความปลอดภัย (ศูนย์ลำปาง)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาอนามัยสิ่งแวดล้อม (ศูนย์รังสิต)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาอนามัยสิ่งแวดล้อม (ศูนย์ลำปาง)",
    "วิทยาศาสตรบัณฑิต สาขาวิชาอนามัยชุมชน"
    ],
  "คณะเภสัชศาสตร์": [
    "เภสัชศาสตรบัณฑิต"
  ],
  "วิทยาลัยแพทยศาสตร์นานาชาติจุฬาภรณ์": [
    "วิทยาศาสตรบัณฑิต สาขาวิชาเทคโนโลยีหัวใจและทรวงอก (นานาชาติ)",
    "การแพทย์แผนจีนบัณฑิต (นานาชาติ)",
    "แพทยศาสตรบัณฑิต และวิทยาศาสตรบัณฑิตสาขาวิชาวิทยาศาสตร์การแพทย์ (นานาชาติ)",
    "ทัศนมาตรศาสตรบัณฑิต (นานาชาติ)"
  ],
};

// --- STATE ---
let users = []; 
let currentView = "General";
let currentPage = 1;
const usersPerPage = 5;
let userIdToDelete = null; 

// --- DOM ELEMENTS ---
const userModal = document.getElementById("userModal");
const confirmModal = document.getElementById("confirmModal"); 
// Form Fields
const userTypeSelect = document.getElementById("userType");
const usernameInput = document.getElementById("username");
const phoneInput = document.getElementById("phone");
const studentIdInput = document.getElementById("studentId");
const identificationIdInput = document.getElementById("identificationId"); // FIX
const passwordInput = document.getElementById("password");
const facultySelect = document.getElementById("faculty"); // FIX
const majorSelect = document.getElementById("major"); // FIX
// Field Groups
const generalFields = document.querySelectorAll(".general-field");
const studentFields = document.querySelectorAll(".student-field");

// --- VIEW TOGGLE ---
document.getElementById("generalViewBtn").addEventListener("click", ()=>{
  currentView="General"; updateToggleUI(); renderTable();
});
document.getElementById("studentViewBtn").addEventListener("click", ()=>{
  currentView="Student"; updateToggleUI(); renderTable();
});
function updateToggleUI(){
  document.getElementById("generalViewBtn").classList.toggle("active", currentView==="General");
  document.getElementById("studentViewBtn").classList.toggle("active", currentView==="Student");
}

// --- SEARCH ---
document.getElementById("searchInput").addEventListener("input", renderTable);

// --- MODAL CONTROLS (USER FORM) ---
const closeUserModal = () => userModal.style.display="none";
document.getElementById("closeModalBtn").addEventListener("click", closeUserModal);
document.getElementById("cancelModalBtn").addEventListener("click", closeUserModal);

// --- MODAL CONTROLS (CONFIRM DELETE) ---
const closeConfirmModal = () => confirmModal.style.display="none";
document.getElementById("closeConfirmModalBtn").addEventListener("click", closeConfirmModal);
document.getElementById("cancelConfirmBtn").addEventListener("click", closeConfirmModal);
document.getElementById("confirmBtn").addEventListener("click", executeDelete); 

// Close modals if clicking outside
window.onclick = e => { 
  if(e.target === userModal) closeUserModal(); 
  if(e.target === confirmModal) closeConfirmModal();
};

// --- ADD USER ---
document.getElementById("addUserBtn").onclick = ()=>{
  document.getElementById("userForm").reset();
  document.getElementById("modalTitle").textContent="Add User";
  document.getElementById("userId").value="";
  
  // Default to General User view
  userTypeSelect.value = "General";
  toggleFormFields("General");
  
  // Enable fields for adding
  studentIdInput.disabled = false;
  identificationIdInput.disabled = false; // FIX
  passwordInput.required = true;
  
  // FIX: Reset dropdowns for Add User
  facultySelect.value = "";
  populateMajorDropdown(""); // This will reset and disable major dropdown
  
  userModal.style.display="flex";
};

// --- FORM LOGIC ---

/**
 * Shows/hides form fields based on User Type
 * @param {string} userType - "General" or "Student"
 */
function toggleFormFields(userType) {
  if (userType === "Student") {
    // Show student fields
    studentFields.forEach(field => field.classList.remove("hidden"));
    // Hide general fields
    generalFields.forEach(field => field.classList.add("hidden"));
    
    // Set required status
    studentIdInput.required = true;
    identificationIdInput.required = true; // FIX
    usernameInput.required = false;
    phoneInput.required = false;

    // Clear general fields
    usernameInput.value = "";
    phoneInput.value = "";

  } else { // General
    // Show general fields
    generalFields.forEach(field => field.classList.remove("hidden"));
    // Hide student fields
    studentFields.forEach(field => field.classList.add("hidden"));
    
    // Set required status
    usernameInput.required = true;
    phoneInput.required = true;
    studentIdInput.required = false;
    identificationIdInput.required = false; // FIX
    
    // Clear student fields
    studentIdInput.value = "";
    identificationIdInput.value = ""; // FIX
    
    // FIX: Reset dropdowns
    facultySelect.value = "";
    majorSelect.value = "";
    populateMajorDropdown(""); // Reset and disable
    
    document.getElementById("year").value = "";
  }
}

// FIX: New function to populate faculty dropdown
function populateFacultyDropdown() {
  facultySelect.innerHTML = ''; // Clear existing
  
  // Add a default "Select Faculty" option
  const defaultOption = document.createElement('option');
  defaultOption.value = "";
  defaultOption.textContent = "Please select a faculty";
  facultySelect.appendChild(defaultOption);

  // Populate with faculties from data
  Object.keys(majorsData).forEach(faculty => {
    const option = document.createElement('option');
    option.value = faculty;
    option.textContent = faculty;
    facultySelect.appendChild(option);
  });
}

// FIX: New function to populate major dropdown based on faculty
function populateMajorDropdown(selectedFaculty) {
  majorSelect.innerHTML = ''; // Clear existing options
  
  if (!selectedFaculty || !majorsData[selectedFaculty]) {
    // If no faculty selected or no majors found, show default and disable
    const option = document.createElement('option');
    option.value = "";
    option.textContent = "Please select a major";
    majorSelect.appendChild(option);
    majorSelect.disabled = true;
  } else {
    // Populate with majors
    const majors = majorsData[selectedFaculty];
    
    // Add a default "Select Major" option
    const defaultOption = document.createElement('option');
    defaultOption.value = "";
    defaultOption.textContent = "Please select a major";
    majorSelect.appendChild(defaultOption);

    // Add majors
    majors.forEach(major => {
      const option = document.createElement('option');
      option.value = major;
      option.textContent = major;
      majorSelect.appendChild(option);
    });
    
    majorSelect.disabled = false; // Enable dropdown
  }
}

// FIX: Add event listener for faculty dropdown
facultySelect.addEventListener("change", () => {
  populateMajorDropdown(facultySelect.value);
});


// Listener for User Type dropdown
userTypeSelect.addEventListener("change", (e) => {
  toggleFormFields(e.target.value);
});

// Form submit (Add or Edit)
document.getElementById("userForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const id = document.getElementById("userId").value;
  const newPassword = passwordInput.value.trim();
  const userType = userTypeSelect.value;

  // 1. Base data
  const data = {
    name: document.getElementById("name").value.trim(), // FIX
    lastname: document.getElementById("lastname").value.trim(), // FIX
    email: document.getElementById("email").value.trim(),
    role: document.getElementById("role").value,
    userType: userType,
  };

  // 2. Add type-specific data
  if (userType === "Student") {
    data.faculty = facultySelect.value.trim(); // FIX
    data.major = majorSelect.value.trim(); // FIX
    data.year = document.getElementById("year").value.trim();

    if (id) {
      // Editing Student: Get read-only IDs from the (disabled) input fields
      data.studentId = studentIdInput.value;
      data.identificationId = identificationIdInput.value; // FIX
    } else {
      // Adding Student: Get IDs from (enabled) input fields
      data.studentId = studentIdInput.value.trim();
      data.identificationId = identificationIdInput.value.trim(); // FIX
    }
  } else { // General
    data.username = usernameInput.value.trim();
    data.phone = phoneInput.value.trim();
  }
  
  // 3. Handle password
  if (newPassword) {
    data.password = newPassword;
  } else if (!id) {
    // Password is required for new users
    return showNotification("Password is required for new users.", "error");
  }
  // If editing and password is blank, we don't send the password field
  // (assuming Back-end keeps old password)

  try {
    let response;
    let url = API_URL;

    // 4. Save (POST for new, PUT for existing)
    if(id){
      // --- UPDATE (PUT) ---
      url = `${API_URL}/${id}`;
      response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) throw new Error(await response.text());
      
      const updatedUser = await response.json();
      users = users.map(u => u.id === updatedUser.id ? updatedUser : u);
      showNotification("User updated successfully","success");

    } else {
      // --- CREATE (POST) ---
      response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) throw new Error(await response.text());
      
      const newUser = await response.json();
      users.push(newUser); 
      showNotification("User added successfully","success");
    }
    
    closeUserModal();
    renderTable(); // Re-render table to show changes

  } catch (error) {
    console.error(`Failed to ${id ? 'update' : 'add'} user:`, error);
    showNotification(`Error: ${error.message}`, "error");
  }
});

// --- EDIT USER ---
function editUser(id){
  const u = users.find(u => u.id === id);
  if(!u) return;

  document.getElementById("userForm").reset();
  userModal.style.display="flex";
  document.getElementById("modalTitle").textContent="Edit User";
  
  // Populate common fields
  document.getElementById("userId").value = u.id;
  document.getElementById("name").value = u.name || ""; // FIX
  document.getElementById("lastname").value = u.lastname || ""; // FIX
  document.getElementById("email").value = u.email;
  document.getElementById("role").value = u.role;
  userTypeSelect.value = u.userType;

  // Toggle fields based on user type
  toggleFormFields(u.userType);

  // Populate type-specific fields
  if (u.userType === "Student") {
    studentIdInput.value = u.studentId || "";
    identificationIdInput.value = u.identificationId || ""; // FIX
    
    // FIX: Set faculty, populate majors, then set major
    facultySelect.value = u.faculty || "";
    populateMajorDropdown(u.faculty || ""); // Populate majors for this faculty
    majorSelect.value = u.major || ""; // Set the saved major
    
    document.getElementById("year").value = u.year || "";
    
    // FIX: Disable ID fields for editing
    studentIdInput.disabled = true;
    identificationIdInput.disabled = true; // FIX

  } else { // General
    usernameInput.value = u.username || "";
    phoneInput.value = u.phone || "";

    // Ensure student fields are enabled (in case they were disabled)
    studentIdInput.disabled = false;
    identificationIdInput.disabled = false; // FIX
  }
  
  passwordInput.value = "";
  passwordInput.required = false; // Password NOT required for editing
}

// --- DELETE USER ---
function deleteUser(id){
  userIdToDelete = id;
  document.getElementById("confirmMessage").textContent = "Are you sure you want to delete this user?";
  document.getElementById("confirmBtn").textContent = "Delete";
  document.getElementById("confirmBtn").className = "danger-btn";
  confirmModal.style.display = "flex";
}

async function executeDelete(){ 
  if (userIdToDelete === null) return;
  
  try {
    const response = await fetch(`${API_URL}/${userIdToDelete}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) throw new Error(await response.text());

    users = users.filter(u => u.id !== userIdToDelete);
    showNotification("User deleted", "success");
    
  } catch (error) {
    console.error('Failed to delete user:', error);
    showNotification(`Error: ${error.message}`, "error");
  } finally {
    userIdToDelete = null;
    closeConfirmModal();
    renderTable(); // Re-render table
  }
}

// --- PAGINATION ---
function paginate(array, page_size, page_number){
  return array.slice((page_number - 1) * page_size, page_number * page_size);
}

// --- FIX: UPDATED FUNCTION TO TOGGLE EXPANDABLE ROW ---
function toggleDetails(id) {
  const detailsRow = document.getElementById(`details-${id}`);
  const btn = document.getElementById(`expand-btn-${id}`);
  
  if (detailsRow && btn) {
    // We use style.display because the 'hidden' class conflicts with
    // the .student-field.hidden logic
    if (detailsRow.style.display === 'table-row') {
      detailsRow.style.display = 'none';
      btn.classList.remove('expanded');
    } else {
      detailsRow.style.display = 'table-row';
      btn.classList.add('expanded');
    }
  }
}

// --- RENDER TABLE ---
function renderTable(){
  const tableHead = document.getElementById("tableHead");
  const tbody = document.querySelector("#userTable tbody");
  let filtered = users.filter(u => u.userType === currentView);

  // FIX: Updated search logic
  const keyword = document.getElementById("searchInput").value.toLowerCase();
  if(keyword){
    filtered = filtered.filter(u => {
      const nameMatch = u.name?.toLowerCase().includes(keyword); // FIX
      const lastnameMatch = u.lastname?.toLowerCase().includes(keyword); // FIX
      const roleMatch = u.role.toLowerCase().includes(keyword);
      
      if (currentView === 'Student') {
        const studentIdMatch = u.studentId?.toLowerCase().includes(keyword);
        const identificationIdMatch = u.identificationId?.toLowerCase().includes(keyword); // FIX
        // FIX: Also search faculty and major
        const facultyMatch = u.faculty?.toLowerCase().includes(keyword);
        const majorMatch = u.major?.toLowerCase().includes(keyword);
        return nameMatch || lastnameMatch || roleMatch || studentIdMatch || identificationIdMatch || facultyMatch || majorMatch; // FIX
      } else { // General
        const usernameMatch = u.username?.toLowerCase().includes(keyword);
        return nameMatch || lastnameMatch || roleMatch || usernameMatch; // FIX
      }
    });
  }

  const totalPages = Math.ceil(filtered.length / usersPerPage);
  if(currentPage > totalPages && totalPages > 0) currentPage = totalPages;
  if(filtered.length === 0) currentPage = 1;
  
  const pageUsers = paginate(filtered, usersPerPage, currentPage);

  // Table head
  if (currentView === "General") {
    tableHead.innerHTML = `
      <tr>
        <th style="width: 40px;"></th> <!-- FIX: Column for expand button -->
        <th>Username</th>
        <th>Name</th>
        <th>Lastname</th>
        <th>Role</th>
        <th class="action-col">Actions</th>
      </tr>`; // FIX
  } else {
    // FIX: Updated Student table head
    tableHead.innerHTML = `
      <tr>
        <th style="width: 40px;"></th> <!-- FIX: Column for expand button -->
        <th>Student ID</th>
        <th>Name</th>
        <th>Lastname</th>
        <th>Role</th>
        <th class="action-col">Actions</th>
      </tr>`; // FIX
  }

  // Table body
  let tableBodyHtml = ""; // Build HTML string manually
  
  if (pageUsers.length === 0) {
    const colCount = 6; // FIX: All tables now have 6 main columns
    tbody.innerHTML = `<tr><td colspan="${colCount}" style="text-align:center; color:#6b7280; padding: 20px;">No users found.</td></tr>`;
  
  } else if (currentView === "General") {
    pageUsers.forEach(u => {
      // --- Main Row ---
      tableBodyHtml += `
        <tr class="main-row">
          <td>
            <!-- FIX: Use standard chevron-up/down -->
            <button class="icon-btn expand-btn" id="expand-btn-${u.id}" onclick="toggleDetails('${u.id}')">
              <i class="fas fa-chevron-down"></i>
            </button>
          </td>
          <td>${u.username}</td>
          <td>${u.name}</td>
          <td>${u.lastname}</td>
          <td>${u.role}</td>
          <td class="action-col">
            <button class="icon-btn edit-btn" title="Edit" onclick="editUser('${u.id}')">
              <i class="fas fa-pen"></i>
            </button>
            <button class="icon-btn delete-btn" title="Delete" onclick="deleteUser('${u.id}')">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>`;
      
      // --- FIX: Details Row (Column-aligned) ---
      tableBodyHtml += `
        <tr class="details-row" id="details-${u.id}" style="display: none;"> <!-- FIX: Corrected typo classf->class -->
          <td></td> <!-- Empty under expand -->
          <td class="details-cell"> <!-- FIX: Moved to Col 2 (under Username) -->
            <strong>Email:</strong>
            <span>${u.email}</span>
          </td>
          <td class="details-cell"> <!-- FIX: Moved to Col 3 (under Name) -->
            <strong>Phone:</strong>
            <span>${u.phone}</span>
          </td>
          <td></td> <!-- Empty under Lastname -->
          <td></td> <!-- Empty under Role -->
          <td></td> <!-- Empty under Actions -->
        </tr>`;
    });
  
  } else { // Student View
    pageUsers.forEach(u => {
      // --- Main Row ---
      tableBodyHtml += `
        <tr class="main-row">
          <td>
            <button class="icon-btn expand-btn" id="expand-btn-${u.id}" onclick="toggleDetails('${u.id}')">
              <i class="fas fa-chevron-down"></i>
            </button>
          </td>
          <td>${u.studentId || "-"}</td>
          <td>${u.name}</td>
          <td>${u.lastname}</td>
          <td>${u.role}</td>
          <td class="action-col">
            <button class="icon-btn edit-btn" title="Edit" onclick="editUser('${u.id}')">
              <i class="fas fa-pen"></i>
            </button>
            <button class="icon-btn delete-btn" title="Delete" onclick="deleteUser('${u.id}')">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>`;
        
      // --- FIX: Details Row (Column-aligned) ---
      // We'll place details in the 5 empty columns
      tableBodyHtml += `
        <tr class="details-row" id="details-${u.id}" style="display: none;">
          <td></td> <!-- Empty under expand -->
          <td class="details-cell">
            <strong>Email:</strong> 
            <span>${u.email}</span>
          </td>
          <td class="details-cell">
            <strong>ID:</strong> 
            <span>${u.identificationId || "-"}</span>
          </td>
          <td class="details-cell">
            <strong>Faculty:</strong> 
            <span>${u.faculty || "-"}</span>
          </td>
          <td class="details-cell">
            <strong>Major:</strong> 
            <span>${u.major || "-"}</span>
          </td>
          <td class="details-cell">
            <strong>Year:</strong> 
            <span>${u.year || "-"}</span>
          </td>
        </tr>`;
    });
  }

  tbody.innerHTML = tableBodyHtml; // Set the generated HTML
  renderPagination(totalPages);
}

// --- RENDER PAGINATION ---
function renderPagination(totalPages){
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";
  for(let i = 1; i <= totalPages; i++){
    const btn = document.createElement("button");
    btn.className = "page-btn" + (i === currentPage ? " active" : "");
    btn.textContent = i;
    btn.onclick = () => { currentPage = i; renderTable(); };
    pagination.appendChild(btn);
  }
}

// --- NOTIFICATION ---
function showNotification(msg, type){
  const noti = document.getElementById("notification");
  noti.textContent=msg;
  noti.className = type === "success" ? "success" : "error";
  noti.style.display="block";
  setTimeout(() => { noti.style.display = "none"; }, 3000);
}

// --- INIT ---
async function fetchAndRenderUsers() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error('Failed to fetch users from server.');
    
    users = await response.json();
    renderTable();

  } catch (error) {
    console.error("Initialization error:", error);
    showNotification(error.message, "error");
    
    // FIX: Updated demo data on failure
    users = [
        {id:1, username:"john (demo)", password:"1234", name:"John (Demo)", lastname: "Doe (Demo)", email:"john@mail.com", phone:"0812345678", role:"User", userType:"General"},
        {id:2, studentId:"6501234567", password:"abcd", name:"Jane (Demo)", lastname: "Smith (Demo)", email:"jane@mail.com", identificationId: "1234567890123", role:"Admin", userType:"Student", faculty:"คณะวิศวกรรมศาสตร์", major:"วิศวกรรมศาสตรบัณฑิต สาขาวิชาวิศวกรรมคอมพิวเตอร์", year:"3"}, // FIX
    ];
    renderTable(); 
  }
}

// Start the app
populateFacultyDropdown(); // FIX: Populate faculties on initial load
fetchAndRenderUsers();
users = users.map(u => ({
    ...u,
    userType: u.userType === "General" || u.userType === "general" ? "General" : "Student"
}));