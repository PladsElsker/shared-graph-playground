const canvas = document.getElementById('graphCanvas');
const context = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const engine = Matter.Engine.create();
const bodies = [];


function toGraphData(pyData) {
    const nodes = [];
    const edges = [];

    pyData.forEach(node => {
        nodes.push({
            id: node.uuid,
            label: node.uuid,
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

const graphData = toGraphData([{"uuid": "16", "children": ["18", "15", "19"], "parents": []}, {"uuid": "19", "children": ["12"], "parents": ["16"]}, {"uuid": "12", "children": ["11"], "parents": ["19", "13", "17"]}, {"uuid": "11", "children": ["10"], "parents": ["12"]}, {"uuid": "10", "children": [], "parents": ["11"]}, {"uuid": "15", "children": ["14"], "parents": ["16"]}, {"uuid": "14", "children": ["13"], "parents": ["15"]}, {"uuid": "13", "children": ["12"], "parents": ["14"]}, {"uuid": "18", "children": ["17"], "parents": ["16"]}, {"uuid": "17", "children": ["12"], "parents": ["18"]}]);

graphData.nodes.forEach(node => {
    const isStatic = node.id === "16";
    let positionX = 0;
    let positionY = 0;
    if(isStatic) {
        positionX = canvas.width / 2;
        positionY = 20;
    }
    else {
        positionX = Math.random() * canvas.width;
        positionY = Math.random() * canvas.height;
    }
    const body = Matter.Bodies.circle(positionX, positionY, 20, {
        label: node.label,
        isStatic: isStatic,
        render: {
            fillStyle: isStatic ? 'red' : 'blue' // Different color for static node
        },
        render: {
            fillStyle: isStatic ? 'red' : 'blue' // Different color for static node
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
            stiffness: 0.005,
            length: 5,
            render: {
                strokeStyle: 'black'
            }
        });
        Matter.World.add(engine.world, line);
    }
});

const centerX = canvas.width / 3;
const centerY = canvas.height / 3;
const dampingFactor = 0.1; 
const forceMagnitude = 0.003; 
const repulsionStrength = 80;
const gravity = 0.003;

function applyRepulsiveForce() {
    for (let i = 0; i < bodies.length; i++) {
        for (let j = i + 1; j < bodies.length; j++) {
            const bodyA = bodies[i];
            const bodyB = bodies[j];

            const dx = bodyB.position.x - bodyA.position.x;
            const dy = bodyB.position.y - bodyA.position.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Apply repulsive force if nodes are too close
            const ddd = distance + 100;
            const force = (repulsionStrength / (ddd * ddd));
            const forceX = (dx / distance) * force;
            const forceY = (dy / distance) * force;

            Matter.Body.applyForce(bodyA, bodyA.position, { x: -forceX, y: -forceY });
            Matter.Body.applyForce(bodyB, bodyB.position, { x: forceX, y: forceY });
        }
    }
}

function render() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    Matter.Engine.update(engine);

    applyRepulsiveForce();

    bodies.forEach(body => {
        body.velocity.x *= (1 - dampingFactor);
        body.velocity.y *= (1 - dampingFactor);

        Matter.Body.applyForce(body, body.position, { x: 0, y: gravity });

        context.beginPath();
        context.arc(body.position.x, body.position.y, 7, 0, Math.PI * 2);
        context.fillStyle = body.render.fillStyle;
        context.fill();
        context.stroke();
        context.closePath();
    });

    const constraints = engine.world.constraints;
    constraints.forEach(constraint => {
        if (constraint.bodyA && constraint.bodyB) {
            context.beginPath();
            context.moveTo(constraint.bodyA.position.x, constraint.bodyA.position.y);
            context.lineTo(constraint.bodyB.position.x, constraint.bodyB.position.y);
            context.strokeStyle = constraint.render.strokeStyle;
            context.stroke();
            context.closePath();
        }
    });

    requestAnimationFrame(render);
}

render();
