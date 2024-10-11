const canvas = document.getElementById('graphCanvas');
const context = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const engine = Matter.Engine.create();

const bodies = [];

const centerX = canvas.width / 2;
const centerY = canvas.height / 2;
const dampingFactor = 0.1;
const forceMagnitude = 0.02;
const repulsionStrength = 0.5;
const gravity = 0;
engine.gravity.x = 0;
engine.gravity.y = 0;
const linkLength = 20;
const bodySize = 10;
const stiffness = 0.02;


function toGraphData(pyData) {
    const nodes = [];
    const edges = [];

    pyData.forEach(node => {
        nodes.push({
            id: node.uuid,
            label: node.uuid,
            operation: node.operation,
        });
        node.children.forEach(child => {
            edges.push({
                source: node.uuid,
                target: child,
            });
        })
    });

    return {
        nodes,
        edges,
    }
}


function bodyToNode(body, nodes) {
    return nodes.find(x => x.id === body.label);
}


const graphData = toGraphData([{"uuid": "633", "children": ["629"], "parents": [], "operation": "Linear.forward"}, {"uuid": "629", "children": ["628"], "parents": ["630", "633"], "operation": "reshape"}, {"uuid": "628", "children": ["627", "626"], "parents": ["629"], "operation": "__getitem__"}, {"uuid": "626", "children": ["624"], "parents": ["628"], "operation": "view"}, {"uuid": "624", "children": ["623", "625"], "parents": ["626"], "operation": "__radd__"}, {"uuid": "625", "children": [], "parents": ["624"], "operation": null}, {"uuid": "623", "children": ["622"], "parents": ["624"], "operation": "view_as_complex"}, {"uuid": "622", "children": ["621"], "parents": ["623"], "operation": "contiguous"}, {"uuid": "621", "children": ["620"], "parents": ["622"], "operation": "permute"}, {"uuid": "620", "children": ["619"], "parents": ["621"], "operation": "reshape"}, {"uuid": "619", "children": ["618", "616"], "parents": ["620"], "operation": "__matmul__"}, {"uuid": "616", "children": ["615"], "parents": ["619"], "operation": "repeat"}, {"uuid": "615", "children": ["614", "612"], "parents": ["616"], "operation": "stack"}, {"uuid": "612", "children": ["613"], "parents": ["615"], "operation": "__getitem__"}, {"uuid": "613", "children": [], "parents": ["614", "612"], "operation": null}, {"uuid": "614", "children": ["613"], "parents": ["615"], "operation": "__getitem__"}, {"uuid": "618", "children": ["617"], "parents": ["619"], "operation": "reshape"}, {"uuid": "617", "children": ["611"], "parents": ["618"], "operation": "permute"}, {"uuid": "611", "children": ["607", "610"], "parents": ["617"], "operation": "bmm"}, {"uuid": "610", "children": ["609"], "parents": ["611"], "operation": "flatten"}, {"uuid": "609", "children": ["608"], "parents": ["610"], "operation": "transpose"}, {"uuid": "608", "children": ["588"], "parents": ["609"], "operation": "view_as_real"}, {"uuid": "588", "children": ["586", "587"], "parents": ["589", "592", "608"], "operation": "__sub__"}, {"uuid": "587", "children": ["586"], "parents": ["588"], "operation": "mean"}, {"uuid": "586", "children": ["551", "585"], "parents": ["588", "587"], "operation": "__add__"}, {"uuid": "585", "children": ["584", "582"], "parents": ["586"], "operation": "complex"}, {"uuid": "582", "children": ["578", "581"], "parents": ["585"], "operation": "__mul__"}, {"uuid": "581", "children": ["580"], "parents": ["582"], "operation": "cos"}, {"uuid": "580", "children": ["579"], "parents": ["581", "583"], "operation": "dropout"}, {"uuid": "579", "children": ["576"], "parents": ["580"], "operation": "angle"}, {"uuid": "576", "children": ["572"], "parents": ["579", "577"], "operation": "Linear.forward"}, {"uuid": "572", "children": ["571", "569"], "parents": ["573", "576"], "operation": "complex"}, {"uuid": "569", "children": ["568", "565"], "parents": ["572"], "operation": "__mul__"}, {"uuid": "565", "children": ["564"], "parents": ["571", "569"], "operation": "dropout"}, {"uuid": "564", "children": ["563"], "parents": ["565"], "operation": "abs"}, {"uuid": "563", "children": ["558", "562"], "parents": ["566", "564"], "operation": "__add__"}, {"uuid": "562", "children": ["561"], "parents": ["563"], "operation": "__rmul__"}, {"uuid": "561", "children": ["559"], "parents": ["562"], "operation": "Softplus.forward"}, {"uuid": "559", "children": ["555"], "parents": ["561", "560"], "operation": "imag"}, {"uuid": "555", "children": ["551"], "parents": ["556", "559"], "operation": "Linear.forward"}, {"uuid": "551", "children": ["549"], "parents": ["555", "586", "552"], "operation": "view"}, {"uuid": "549", "children": ["548", "550"], "parents": ["551"], "operation": "__radd__"}, {"uuid": "550", "children": [], "parents": ["549"], "operation": null}, {"uuid": "548", "children": ["547"], "parents": ["549"], "operation": "view_as_complex"}, {"uuid": "547", "children": ["546"], "parents": ["548"], "operation": "contiguous"}, {"uuid": "546", "children": ["545"], "parents": ["547"], "operation": "permute"}, {"uuid": "545", "children": ["544"], "parents": ["546"], "operation": "reshape"}, {"uuid": "544", "children": ["541", "543"], "parents": ["545"], "operation": "__matmul__"}, {"uuid": "543", "children": ["542"], "parents": ["544"], "operation": "reshape"}, {"uuid": "542", "children": ["536"], "parents": ["543"], "operation": "permute"}, {"uuid": "536", "children": ["532", "535"], "parents": ["542"], "operation": "bmm"}, {"uuid": "535", "children": ["534"], "parents": ["536"], "operation": "flatten"}, {"uuid": "534", "children": ["533"], "parents": ["535"], "operation": "transpose"}, {"uuid": "533", "children": ["513"], "parents": ["534"], "operation": "view_as_real"}, {"uuid": "513", "children": ["512", "511"], "parents": ["514", "517", "533"], "operation": "__sub__"}, {"uuid": "511", "children": ["510", "453"], "parents": ["513", "512"], "operation": "__add__"}, {"uuid": "453", "children": ["451"], "parents": ["471", "511", "457", "464", "468", "454", "461"], "operation": "view"}, {"uuid": "451", "children": ["452", "450"], "parents": ["453"], "operation": "__radd__"}, {"uuid": "450", "children": ["449"], "parents": ["451"], "operation": "view_as_complex"}, {"uuid": "449", "children": ["448"], "parents": ["450"], "operation": "contiguous"}, {"uuid": "448", "children": ["447"], "parents": ["449"], "operation": "permute"}, {"uuid": "447", "children": ["446"], "parents": ["448"], "operation": "reshape"}, {"uuid": "446", "children": ["445", "443"], "parents": ["447"], "operation": "__matmul__"}, {"uuid": "443", "children": ["442"], "parents": ["446"], "operation": "repeat"}, {"uuid": "442", "children": ["439", "441"], "parents": ["443"], "operation": "stack"}, {"uuid": "441", "children": ["440"], "parents": ["442"], "operation": "__getitem__"}, {"uuid": "440", "children": [], "parents": ["439", "441"], "operation": null}, {"uuid": "439", "children": ["440"], "parents": ["442"], "operation": "__getitem__"}, {"uuid": "445", "children": ["444"], "parents": ["446"], "operation": "reshape"}, {"uuid": "444", "children": ["438"], "parents": ["445"], "operation": "permute"}, {"uuid": "438", "children": ["434", "437"], "parents": ["444"], "operation": "bmm"}, {"uuid": "437", "children": ["436"], "parents": ["438"], "operation": "flatten"}, {"uuid": "436", "children": ["435"], "parents": ["437"], "operation": "transpose"}, {"uuid": "435", "children": ["415"], "parents": ["436"], "operation": "view_as_real"}, {"uuid": "415", "children": ["413", "414"], "parents": ["416", "435", "419"], "operation": "__sub__"}, {"uuid": "414", "children": ["413"], "parents": ["415"], "operation": "mean"}, {"uuid": "413", "children": ["378", "412"], "parents": ["415", "414"], "operation": "__add__"}, {"uuid": "412", "children": ["411", "409"], "parents": ["413"], "operation": "complex"}, {"uuid": "409", "children": ["408", "405"], "parents": ["412"], "operation": "__mul__"}, {"uuid": "405", "children": ["404"], "parents": ["411", "409"], "operation": "dropout"}, {"uuid": "404", "children": ["403"], "parents": ["405"], "operation": "abs"}, {"uuid": "403", "children": ["399"], "parents": ["404", "406"], "operation": "Linear.forward"}, {"uuid": "399", "children": ["398", "396"], "parents": ["400", "403"], "operation": "complex"}, {"uuid": "396", "children": ["395", "392"], "parents": ["399"], "operation": "__mul__"}, {"uuid": "392", "children": ["391"], "parents": ["398", "396"], "operation": "dropout"}, {"uuid": "391", "children": ["390"], "parents": ["392"], "operation": "abs"}, {"uuid": "390", "children": ["385", "389"], "parents": ["391", "393"], "operation": "__add__"}, {"uuid": "389", "children": ["388"], "parents": ["390"], "operation": "__rmul__"}, {"uuid": "388", "children": ["386"], "parents": ["389"], "operation": "Softplus.forward"}, {"uuid": "386", "children": ["382"], "parents": ["387", "388"], "operation": "imag"}, {"uuid": "382", "children": ["378"], "parents": ["386", "383"], "operation": "Linear.forward"}, {"uuid": "378", "children": ["376"], "parents": ["379", "413", "382"], "operation": "view"}, {"uuid": "376", "children": ["377", "375"], "parents": ["378"], "operation": "__radd__"}, {"uuid": "375", "children": ["374"], "parents": ["376"], "operation": "view_as_complex"}, {"uuid": "374", "children": ["373"], "parents": ["375"], "operation": "contiguous"}, {"uuid": "373", "children": ["372"], "parents": ["374"], "operation": "permute"}, {"uuid": "372", "children": ["371"], "parents": ["373"], "operation": "reshape"}, {"uuid": "371", "children": ["370", "368"], "parents": ["372"], "operation": "__matmul__"}, {"uuid": "368", "children": ["367"], "parents": ["371"], "operation": "repeat"}, {"uuid": "367", "children": ["366", "364"], "parents": ["368"], "operation": "stack"}, {"uuid": "364", "children": ["365"], "parents": ["367"], "operation": "__getitem__"}, {"uuid": "365", "children": [], "parents": ["366", "364"], "operation": null}, {"uuid": "366", "children": ["365"], "parents": ["367"], "operation": "__getitem__"}, {"uuid": "370", "children": ["369"], "parents": ["371"], "operation": "reshape"}, {"uuid": "369", "children": ["363"], "parents": ["370"], "operation": "permute"}, {"uuid": "363", "children": ["359", "362"], "parents": ["369"], "operation": "bmm"}, {"uuid": "362", "children": ["361"], "parents": ["363"], "operation": "flatten"}, {"uuid": "361", "children": ["360"], "parents": ["362"], "operation": "transpose"}, {"uuid": "360", "children": ["340"], "parents": ["361"], "operation": "view_as_real"}, {"uuid": "340", "children": ["338", "339"], "parents": ["344", "341", "360"], "operation": "__sub__"}, {"uuid": "339", "children": ["338"], "parents": ["340"], "operation": "mean"}, {"uuid": "338", "children": ["337", "280"], "parents": ["340", "339"], "operation": "__add__"}, {"uuid": "280", "children": ["278", "279"], "parents": ["338", "284", "291", "295", "281", "298", "288"], "operation": "__getitem__"}, {"uuid": "279", "children": ["16"], "parents": ["280"], "operation": "reshape"}, {"uuid": "16", "children": ["13", "15"], "parents": ["279"], "operation": "complex"}, {"uuid": "15", "children": ["9", "14"], "parents": ["16"], "operation": "__mul__"}, {"uuid": "14", "children": ["11"], "parents": ["15"], "operation": "sin"}, {"uuid": "11", "children": ["10"], "parents": ["12", "14"], "operation": "dropout"}, {"uuid": "10", "children": ["7"], "parents": ["11"], "operation": "angle"}, {"uuid": "7", "children": ["5", "4"], "parents": ["8", "10"], "operation": "__add__"}, {"uuid": "4", "children": ["0"], "parents": ["7"], "operation": "Linear.forward"}, {"uuid": "0", "children": [], "parents": ["1", "4"], "operation": "root"}, {"uuid": "5", "children": ["6"], "parents": ["7"], "operation": "__getitem__"}, {"uuid": "6", "children": [], "parents": ["5"], "operation": null}, {"uuid": "9", "children": ["8"], "parents": ["13", "15"], "operation": "dropout"}, {"uuid": "8", "children": ["7"], "parents": ["9"], "operation": "abs"}, {"uuid": "13", "children": ["9", "12"], "parents": ["16"], "operation": "__mul__"}, {"uuid": "12", "children": ["11"], "parents": ["13"], "operation": "cos"}, {"uuid": "278", "children": ["277"], "parents": ["627", "280"], "operation": "flatten"}, {"uuid": "277", "children": ["18", "276"], "parents": ["278"], "operation": "cat"}, {"uuid": "276", "children": ["17"], "parents": ["277"], "operation": "flip"}, {"uuid": "17", "children": [], "parents": ["151", "122", "215", "51", "83", "52", "118", "88", "227", "198", "180", "228", "24", "234", "90", "22", "167", "84", "259", "186", "131", "58", "230", "264", "104", "115", "250", "168", "183", "276", "246", "42", "199", "26", "68", "86", "136", "134", "243", "150", "19", "38", "67", "106", "247", "148", "272", "132", "244", "135", "36", "154", "200", "266", "99", "119", "182", "103", "196", "71", "100", "120", "20", "152", "195", "214", "216", "262", "35", "232", "138", "40", "147", "211", "218", "184", "231", "87", "116", "273", "166", "260", "74", "56", "102", "23", "263", "248", "55", "164", "202", "170", "163", "70", "54", "39", "212", "179", "72"], "operation": "zeros"}, {"uuid": "18", "children": [], "parents": ["91", "268", "206", "76", "110", "128", "62", "174", "127", "258", "275", "107", "59", "139", "142", "31", "274", "158", "207", "112", "48", "160", "144", "78", "210", "219", "239", "79", "277", "270", "92", "162", "176", "47", "251", "66", "123", "252", "187", "242", "75", "208", "50", "156", "159", "130", "98", "34", "111", "254", "171", "124", "220", "223", "222", "64", "267", "178", "172", "27", "203", "63", "271", "114", "126", "28", "191", "255", "235", "94", "95", "82", "43", "108", "32", "30", "44", "140", "192", "240", "155", "224", "190", "60", "146", "188", "238", "204", "256", "175", "46", "143", "80", "226", "194", "236", "96"], "operation": "zeros"}, {"uuid": "337", "children": ["336", "334"], "parents": ["338"], "operation": "complex"}, {"uuid": "334", "children": ["330", "333"], "parents": ["337"], "operation": "__mul__"}, {"uuid": "333", "children": ["332"], "parents": ["334"], "operation": "cos"}, {"uuid": "332", "children": ["331"], "parents": ["333", "335"], "operation": "dropout"}, {"uuid": "331", "children": ["328"], "parents": ["332"], "operation": "angle"}, {"uuid": "328", "children": ["324"], "parents": ["329", "331"], "operation": "Linear.forward"}, {"uuid": "324", "children": ["323", "321"], "parents": ["328", "325"], "operation": "complex"}, {"uuid": "321", "children": ["320", "317"], "parents": ["324"], "operation": "__mul__"}, {"uuid": "317", "children": ["316"], "parents": ["323", "321"], "operation": "dropout"}, {"uuid": "316", "children": ["315"], "parents": ["317"], "operation": "abs"}, {"uuid": "315", "children": ["314"], "parents": ["318", "316"], "operation": "reshape"}, {"uuid": "314", "children": ["313"], "parents": ["315"], "operation": "permute"}, {"uuid": "313", "children": ["312"], "parents": ["314"], "operation": "view"}, {"uuid": "312", "children": ["311", "301"], "parents": ["313"], "operation": "bmm"}, {"uuid": "301", "children": ["300"], "parents": ["312"], "operation": "reshape"}, {"uuid": "300", "children": ["299"], "parents": ["301"], "operation": "permute"}, {"uuid": "299", "children": ["298"], "parents": ["300"], "operation": "view"}, {"uuid": "298", "children": ["280"], "parents": ["299"], "operation": "Linear.forward"}, {"uuid": "311", "children": ["309", "310"], "parents": ["312"], "operation": "__truediv__"}, {"uuid": "310", "children": ["309"], "parents": ["311"], "operation": "sum"}, {"uuid": "309", "children": ["308"], "parents": ["311", "310"], "operation": "exp"}, {"uuid": "308", "children": ["305", "307"], "parents": ["309"], "operation": "__sub__"}, {"uuid": "307", "children": ["306"], "parents": ["308"], "operation": "max"}, {"uuid": "306", "children": ["305"], "parents": ["307"], "operation": "real"}, {"uuid": "305", "children": ["304"], "parents": ["306", "308"], "operation": "__truediv__"}, {"uuid": "304", "children": ["287", "303"], "parents": ["305"], "operation": "bmm"}, {"uuid": "303", "children": ["302"], "parents": ["304"], "operation": "transpose"}, {"uuid": "302", "children": ["294"], "parents": ["303"], "operation": "conj"}, {"uuid": "294", "children": ["293"], "parents": ["302"], "operation": "reshape"}, {"uuid": "293", "children": ["292"], "parents": ["294"], "operation": "permute"}, {"uuid": "292", "children": ["291"], "parents": ["293"], "operation": "view"}, {"uuid": "291", "children": ["280"], "parents": ["292"], "operation": "Linear.forward"}, {"uuid": "287", "children": ["286"], "parents": ["304"], "operation": "reshape"}, {"uuid": "286", "children": ["285"], "parents": ["287"], "operation": "permute"}, {"uuid": "285", "children": ["284"], "parents": ["286"], "operation": "view"}, {"uuid": "284", "children": ["280"], "parents": ["285"], "operation": "Linear.forward"}, {"uuid": "320", "children": ["319"], "parents": ["321"], "operation": "cos"}, {"uuid": "319", "children": ["318"], "parents": ["320", "322"], "operation": "dropout"}, {"uuid": "318", "children": ["315"], "parents": ["319"], "operation": "angle"}, {"uuid": "323", "children": ["322", "317"], "parents": ["324"], "operation": "__mul__"}, {"uuid": "322", "children": ["319"], "parents": ["323"], "operation": "sin"}, {"uuid": "330", "children": ["329"], "parents": ["336", "334"], "operation": "dropout"}, {"uuid": "329", "children": ["328"], "parents": ["330"], "operation": "abs"}, {"uuid": "336", "children": ["330", "335"], "parents": ["337"], "operation": "__mul__"}, {"uuid": "335", "children": ["332"], "parents": ["336"], "operation": "sin"}, {"uuid": "359", "children": ["357", "358"], "parents": ["363"], "operation": "bmm"}, {"uuid": "358", "children": ["351"], "parents": ["359"], "operation": "inv"}, {"uuid": "351", "children": ["350"], "parents": ["352", "357", "358"], "operation": "eigh"}, {"uuid": "350", "children": ["347", "349"], "parents": ["351"], "operation": "__add__"}, {"uuid": "349", "children": ["348"], "parents": ["350"], "operation": "diag"}, {"uuid": "348", "children": [], "parents": ["349"], "operation": "tensor"}, {"uuid": "347", "children": ["346"], "parents": ["350"], "operation": "__truediv__"}, {"uuid": "346", "children": ["343", "345"], "parents": ["347"], "operation": "bmm"}, {"uuid": "345", "children": ["344"], "parents": ["346"], "operation": "reshape"}, {"uuid": "344", "children": ["340"], "parents": ["345"], "operation": "view_as_real"}, {"uuid": "343", "children": ["342"], "parents": ["346"], "operation": "reshape"}, {"uuid": "342", "children": ["341"], "parents": ["343"], "operation": "transpose"}, {"uuid": "341", "children": ["340"], "parents": ["342"], "operation": "view_as_real"}, {"uuid": "357", "children": ["351", "356"], "parents": ["359"], "operation": "bmm"}, {"uuid": "356", "children": ["355"], "parents": ["357"], "operation": "diag_embed"}, {"uuid": "355", "children": ["352"], "parents": ["356"], "operation": "__rtruediv__"}, {"uuid": "352", "children": ["351"], "parents": ["353", "355"], "operation": "sqrt"}, {"uuid": "377", "children": [], "parents": ["376"], "operation": null}, {"uuid": "385", "children": ["383"], "parents": ["390"], "operation": "Softplus.forward"}, {"uuid": "383", "children": ["382"], "parents": ["385", "384"], "operation": "real"}, {"uuid": "395", "children": ["394"], "parents": ["396"], "operation": "cos"}, {"uuid": "394", "children": ["393"], "parents": ["397", "395"], "operation": "dropout"}, {"uuid": "393", "children": ["390"], "parents": ["394"], "operation": "angle"}, {"uuid": "398", "children": ["397", "392"], "parents": ["399"], "operation": "__mul__"}, {"uuid": "397", "children": ["394"], "parents": ["398"], "operation": "sin"}, {"uuid": "408", "children": ["407"], "parents": ["409"], "operation": "cos"}, {"uuid": "407", "children": ["406"], "parents": ["408", "410"], "operation": "dropout"}, {"uuid": "406", "children": ["403"], "parents": ["407"], "operation": "angle"}, {"uuid": "411", "children": ["405", "410"], "parents": ["412"], "operation": "__mul__"}, {"uuid": "410", "children": ["407"], "parents": ["411"], "operation": "sin"}, {"uuid": "434", "children": ["432", "433"], "parents": ["438"], "operation": "bmm"}, {"uuid": "433", "children": ["426"], "parents": ["434"], "operation": "inv"}, {"uuid": "426", "children": ["425"], "parents": ["432", "427", "433"], "operation": "eigh"}, {"uuid": "425", "children": ["422", "424"], "parents": ["426"], "operation": "__add__"}, {"uuid": "424", "children": ["423"], "parents": ["425"], "operation": "diag"}, {"uuid": "423", "children": [], "parents": ["424"], "operation": "tensor"}, {"uuid": "422", "children": ["421"], "parents": ["425"], "operation": "__truediv__"}, {"uuid": "421", "children": ["418", "420"], "parents": ["422"], "operation": "bmm"}, {"uuid": "420", "children": ["419"], "parents": ["421"], "operation": "reshape"}, {"uuid": "419", "children": ["415"], "parents": ["420"], "operation": "view_as_real"}, {"uuid": "418", "children": ["417"], "parents": ["421"], "operation": "reshape"}, {"uuid": "417", "children": ["416"], "parents": ["418"], "operation": "transpose"}, {"uuid": "416", "children": ["415"], "parents": ["417"], "operation": "view_as_real"}, {"uuid": "432", "children": ["431", "426"], "parents": ["434"], "operation": "bmm"}, {"uuid": "431", "children": ["430"], "parents": ["432"], "operation": "diag_embed"}, {"uuid": "430", "children": ["427"], "parents": ["431"], "operation": "__rtruediv__"}, {"uuid": "427", "children": ["426"], "parents": ["430", "428"], "operation": "sqrt"}, {"uuid": "452", "children": [], "parents": ["451"], "operation": null}, {"uuid": "510", "children": ["509", "507"], "parents": ["511"], "operation": "complex"}, {"uuid": "507", "children": ["506", "503"], "parents": ["510"], "operation": "__mul__"}, {"uuid": "503", "children": ["502"], "parents": ["509", "507"], "operation": "dropout"}, {"uuid": "502", "children": ["501"], "parents": ["503"], "operation": "abs"}, {"uuid": "501", "children": ["497"], "parents": ["502", "504"], "operation": "Linear.forward"}, {"uuid": "497", "children": ["496", "494"], "parents": ["501", "498"], "operation": "complex"}, {"uuid": "494", "children": ["493", "490"], "parents": ["497"], "operation": "__mul__"}, {"uuid": "490", "children": ["489"], "parents": ["496", "494"], "operation": "dropout"}, {"uuid": "489", "children": ["488"], "parents": ["490"], "operation": "abs"}, {"uuid": "488", "children": ["487"], "parents": ["489", "491"], "operation": "reshape"}, {"uuid": "487", "children": ["486"], "parents": ["488"], "operation": "permute"}, {"uuid": "486", "children": ["485"], "parents": ["487"], "operation": "view"}, {"uuid": "485", "children": ["474", "484"], "parents": ["486"], "operation": "bmm"}, {"uuid": "484", "children": ["482", "483"], "parents": ["485"], "operation": "__truediv__"}, {"uuid": "483", "children": ["482"], "parents": ["484"], "operation": "sum"}, {"uuid": "482", "children": ["481"], "parents": ["484", "483"], "operation": "exp"}, {"uuid": "481", "children": ["480", "478"], "parents": ["482"], "operation": "__sub__"}, {"uuid": "478", "children": ["477"], "parents": ["479", "481"], "operation": "__truediv__"}, {"uuid": "477", "children": ["460", "476"], "parents": ["478"], "operation": "bmm"}, {"uuid": "476", "children": ["475"], "parents": ["477"], "operation": "transpose"}, {"uuid": "475", "children": ["467"], "parents": ["476"], "operation": "conj"}, {"uuid": "467", "children": ["466"], "parents": ["475"], "operation": "reshape"}, {"uuid": "466", "children": ["465"], "parents": ["467"], "operation": "permute"}, {"uuid": "465", "children": ["464"], "parents": ["466"], "operation": "view"}, {"uuid": "464", "children": ["453"], "parents": ["465"], "operation": "Linear.forward"}, {"uuid": "460", "children": ["459"], "parents": ["477"], "operation": "reshape"}, {"uuid": "459", "children": ["458"], "parents": ["460"], "operation": "permute"}, {"uuid": "458", "children": ["457"], "parents": ["459"], "operation": "view"}, {"uuid": "457", "children": ["453"], "parents": ["458"], "operation": "Linear.forward"}, {"uuid": "480", "children": ["479"], "parents": ["481"], "operation": "max"}, {"uuid": "479", "children": ["478"], "parents": ["480"], "operation": "real"}, {"uuid": "474", "children": ["473"], "parents": ["485"], "operation": "reshape"}, {"uuid": "473", "children": ["472"], "parents": ["474"], "operation": "permute"}, {"uuid": "472", "children": ["471"], "parents": ["473"], "operation": "view"}, {"uuid": "471", "children": ["453"], "parents": ["472"], "operation": "Linear.forward"}, {"uuid": "493", "children": ["492"], "parents": ["494"], "operation": "cos"}, {"uuid": "492", "children": ["491"], "parents": ["495", "493"], "operation": "dropout"}, {"uuid": "491", "children": ["488"], "parents": ["492"], "operation": "angle"}, {"uuid": "496", "children": ["495", "490"], "parents": ["497"], "operation": "__mul__"}, {"uuid": "495", "children": ["492"], "parents": ["496"], "operation": "sin"}, {"uuid": "506", "children": ["505"], "parents": ["507"], "operation": "cos"}, {"uuid": "505", "children": ["504"], "parents": ["506", "508"], "operation": "dropout"}, {"uuid": "504", "children": ["501"], "parents": ["505"], "operation": "angle"}, {"uuid": "509", "children": ["508", "503"], "parents": ["510"], "operation": "__mul__"}, {"uuid": "508", "children": ["505"], "parents": ["509"], "operation": "sin"}, {"uuid": "512", "children": ["511"], "parents": ["513"], "operation": "mean"}, {"uuid": "532", "children": ["530", "531"], "parents": ["536"], "operation": "bmm"}, {"uuid": "531", "children": ["524"], "parents": ["532"], "operation": "inv"}, {"uuid": "524", "children": ["523"], "parents": ["530", "525", "531"], "operation": "eigh"}, {"uuid": "523", "children": ["520", "522"], "parents": ["524"], "operation": "__add__"}, {"uuid": "522", "children": ["521"], "parents": ["523"], "operation": "diag"}, {"uuid": "521", "children": [], "parents": ["522"], "operation": "tensor"}, {"uuid": "520", "children": ["519"], "parents": ["523"], "operation": "__truediv__"}, {"uuid": "519", "children": ["518", "516"], "parents": ["520"], "operation": "bmm"}, {"uuid": "516", "children": ["515"], "parents": ["519"], "operation": "reshape"}, {"uuid": "515", "children": ["514"], "parents": ["516"], "operation": "transpose"}, {"uuid": "514", "children": ["513"], "parents": ["515"], "operation": "view_as_real"}, {"uuid": "518", "children": ["517"], "parents": ["519"], "operation": "reshape"}, {"uuid": "517", "children": ["513"], "parents": ["518"], "operation": "view_as_real"}, {"uuid": "530", "children": ["529", "524"], "parents": ["532"], "operation": "bmm"}, {"uuid": "529", "children": ["528"], "parents": ["530"], "operation": "diag_embed"}, {"uuid": "528", "children": ["525"], "parents": ["529"], "operation": "__rtruediv__"}, {"uuid": "525", "children": ["524"], "parents": ["526", "528"], "operation": "sqrt"}, {"uuid": "541", "children": ["540"], "parents": ["544"], "operation": "repeat"}, {"uuid": "540", "children": ["537", "539"], "parents": ["541"], "operation": "stack"}, {"uuid": "539", "children": ["538"], "parents": ["540"], "operation": "__getitem__"}, {"uuid": "538", "children": [], "parents": ["537", "539"], "operation": null}, {"uuid": "537", "children": ["538"], "parents": ["540"], "operation": "__getitem__"}, {"uuid": "558", "children": ["556"], "parents": ["563"], "operation": "Softplus.forward"}, {"uuid": "556", "children": ["555"], "parents": ["557", "558"], "operation": "real"}, {"uuid": "568", "children": ["567"], "parents": ["569"], "operation": "cos"}, {"uuid": "567", "children": ["566"], "parents": ["570", "568"], "operation": "dropout"}, {"uuid": "566", "children": ["563"], "parents": ["567"], "operation": "angle"}, {"uuid": "571", "children": ["570", "565"], "parents": ["572"], "operation": "__mul__"}, {"uuid": "570", "children": ["567"], "parents": ["571"], "operation": "sin"}, {"uuid": "578", "children": ["577"], "parents": ["584", "582"], "operation": "dropout"}, {"uuid": "577", "children": ["576"], "parents": ["578"], "operation": "abs"}, {"uuid": "584", "children": ["578", "583"], "parents": ["585"], "operation": "__mul__"}, {"uuid": "583", "children": ["580"], "parents": ["584"], "operation": "sin"}, {"uuid": "607", "children": ["605", "606"], "parents": ["611"], "operation": "bmm"}, {"uuid": "606", "children": ["599"], "parents": ["607"], "operation": "inv"}, {"uuid": "599", "children": ["598"], "parents": ["600", "606", "605"], "operation": "eigh"}, {"uuid": "598", "children": ["597", "595"], "parents": ["599"], "operation": "__add__"}, {"uuid": "595", "children": ["594"], "parents": ["598"], "operation": "__truediv__"}, {"uuid": "594", "children": ["593", "591"], "parents": ["595"], "operation": "bmm"}, {"uuid": "591", "children": ["590"], "parents": ["594"], "operation": "reshape"}, {"uuid": "590", "children": ["589"], "parents": ["591"], "operation": "transpose"}, {"uuid": "589", "children": ["588"], "parents": ["590"], "operation": "view_as_real"}, {"uuid": "593", "children": ["592"], "parents": ["594"], "operation": "reshape"}, {"uuid": "592", "children": ["588"], "parents": ["593"], "operation": "view_as_real"}, {"uuid": "597", "children": ["596"], "parents": ["598"], "operation": "diag"}, {"uuid": "596", "children": [], "parents": ["597"], "operation": "tensor"}, {"uuid": "605", "children": ["599", "604"], "parents": ["607"], "operation": "bmm"}, {"uuid": "604", "children": ["603"], "parents": ["605"], "operation": "diag_embed"}, {"uuid": "603", "children": ["600"], "parents": ["604"], "operation": "__rtruediv__"}, {"uuid": "600", "children": ["599"], "parents": ["601", "603"], "operation": "sqrt"}, {"uuid": "627", "children": ["278"], "parents": ["628"], "operation": "argsort"}]);

const rootId = graphData.nodes[0].id;

graphData.nodes.forEach(node => {
    const isStatic = node.id === rootId;
    const isRoot = (bodyToNode({label: node.label}, graphData.nodes)??{operation: undefined}).operation === 'root';
    let positionX = 0;
    let positionY = 0;
    if(isStatic) {
        positionX = centerX;
        positionY = centerY * 3;
    }
    else if(isRoot) {
        positionX = centerX;
        positionY = -centerY;
    }
    else {
        positionX = Math.random() * canvas.width + (centerX - canvas.width/2);
        positionY = Math.random() * canvas.height + (centerY - canvas.height/2);
    }
    let color = 'blue';
    if(isStatic) {
        color = 'red';
    }
    if(isRoot) {
        color = 'green';
    }
    const body = Matter.Bodies.circle(positionX, positionY, bodySize, {
        label: node.label,
        isStatic: isRoot,
        render: {
            fillStyle: color,
        }
    });
    bodies.push(body);
    Matter.World.add(engine.world, body);
});

graphData.edges.forEach(edge => {
    const source = bodies.find(b => b.label === edge.source);
    const target = bodies.find(b => b.label === edge.target);
    
    if (source && target) {
        const line = Matter.Constraint.create({
            bodyA: source,
            bodyB: target,
            stiffness: stiffness,
            length: linkLength,
            render: {
                strokeStyle: 'black'
            }
        });
        Matter.World.add(engine.world, line);
    }
});

function applyRepulsiveForce() {
    for (let i = 0; i < bodies.length; i++) {
        for (let j = i + 1; j < bodies.length; j++) {
            const bodyA = bodies[i];
            const bodyB = bodies[j];

            const dx = bodyB.position.x - bodyA.position.x;
            const dy = bodyB.position.y - bodyA.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Apply repulsive force if nodes are too close
            const ddd = distance + 80;
            const force = (repulsionStrength / (ddd * ddd));
            const forceX = (dx / distance) * force;
            const forceY = (dy / distance) * force;

            Matter.Body.applyForce(bodyA, bodyA.position, { x: -forceX, y: -forceY });
            Matter.Body.applyForce(bodyB, bodyB.position, { x: forceX, y: forceY });
        }
    }
}

let cameraX = 0;
let cameraY = 0;
let scale = 1;

document.addEventListener('wheel', (event) => {
    const delta = event.deltaY > 0 ? 0.9 : 1.1;

    const previousScale = scale;
    scale *= delta;

    const mouseX = event.clientX;
    const mouseY = event.clientY;

    cameraX = (cameraX / previousScale + mouseX * (1/scale - 1/previousScale)) * scale;
    cameraY = (cameraY / previousScale + mouseY * (1/scale - 1/previousScale)) * scale;
});

function render() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    Matter.Engine.update(engine);

    applyRepulsiveForce();

    context.save();

    context.translate(cameraX, cameraY);
    context.scale(scale, scale);

    // Draw the bodies (nodes)
    bodies.forEach(body => {
        body.velocity.x *= (1 - dampingFactor);
        body.velocity.y *= (1 - dampingFactor);
        Matter.Body.applyForce(body, body.position, { x: 0, y: gravity });

        context.beginPath();
        context.arc(body.position.x, body.position.y, bodySize, 0, Math.PI * 2);
        context.fillStyle = body.render.fillStyle;
        context.fill();
        context.stroke();
        context.closePath();
    });

    // Draw the constraints (edges) with arrows for direction
    graphData.edges.forEach(edge => {
        const source = bodies.find(b => b.label === edge.source);
        const target = bodies.find(b => b.label === edge.target);

        if (source && target) {
            // Draw the edge line
            context.beginPath();
            context.moveTo(target.position.x, target.position.y);
            context.lineTo(source.position.x, source.position.y);
            context.strokeStyle = 'black';
            context.stroke();
            context.closePath();

            // Draw an arrow to show the direction
            drawArrow(target.position, source.position);
        }
    });

    context.restore();

    requestAnimationFrame(render);
}

function drawArrow(start, end) {
    const arrowLength = 15;
    const arrowWidth = 7;

    // Calculate the direction vector
    const dx = end.x - start.x;
    const dy = end.y - start.y;
    const angle = Math.atan2(dy, dx);

    // Draw the line
    context.beginPath();
    context.moveTo(end.x, end.y);

    // Calculate the arrowhead points
    const arrowPoint1 = {
        x: end.x - arrowLength * Math.cos(angle - Math.PI / 6),
        y: end.y - arrowLength * Math.sin(angle - Math.PI / 6),
    };

    const arrowPoint2 = {
        x: end.x - arrowLength * Math.cos(angle + Math.PI / 6),
        y: end.y - arrowLength * Math.sin(angle + Math.PI / 6),
    };

    // Draw the arrowhead
    context.lineTo(arrowPoint1.x, arrowPoint1.y);
    context.moveTo(end.x, end.y);
    context.lineTo(arrowPoint2.x, arrowPoint2.y);
    context.stroke();
    context.closePath();
}

render();


const overlays = Array.from(document.getElementsByClassName('overlay'));

document.addEventListener('mousemove', (event) => {
    const mouseX = event.clientX;
    const mouseY = event.clientY;

    let hoveredBody = null;

    bodies.forEach(body => {
        const globMousePosX = - cameraX / scale + mouseX / scale;
        const globMousePosY = - cameraY / scale + mouseY / scale;
        const distance = Math.sqrt(
            Math.pow(body.position.x - globMousePosX, 2) +
            Math.pow(body.position.y - globMousePosY, 2)
        );

        if (distance < bodySize) {
            hoveredBody = body;
        }
    });

    overlays.forEach(overlay => {
        if(hoveredBody) {
            overlay.style.display = 'block';
            overlay.innerHTML = (bodyToNode(hoveredBody, graphData.nodes)??{operation: undefined}).operation;
            overlay.style.left = `${event.clientX + 10}px`;
            overlay.style.top = `${event.clientY + 10}px`;
        }
        else {
            overlay.style.display = 'none';
        }
    });
});


overlays.forEach(overlay => {
    canvas.addEventListener('mouseleave', () => {
        overlay.style.display = 'none';
    });
});