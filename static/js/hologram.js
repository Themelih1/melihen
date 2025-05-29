import * as THREE from 'three';

class HologramEffect {
  constructor() {
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
    this.renderer = new THREE.WebGLRenderer({ alpha: true });
    
    this.init();
  }

  init() {
    // Geometri ve Materyal
    const geometry = new THREE.IcosahedronGeometry(2, 15);
    const material = new THREE.MeshPhongMaterial({
      color: 0x00ff00,
      shininess: 100,
      wireframe: true
    });
    
    this.mesh = new THREE.Mesh(geometry, material);
    this.scene.add(this.mesh);
    
    // Işıklandırma
    const light = new THREE.PointLight(0x00ff00, 1, 100);
    light.position.set(10, 10, 10);
    this.scene.add(light);
    
    // Render
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.querySelector('#hologram-container').appendChild(this.renderer.domElement);
    
    // Animasyon
    this.animate();
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.mesh.rotation.x += 0.01;
    this.mesh.rotation.y += 0.01;
    this.renderer.render(this.scene, this.camera);
  }
}

new HologramEffect();