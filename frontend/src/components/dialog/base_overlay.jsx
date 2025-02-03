import './base_overlay.css';

export default function BaseOverlay({children, onClick}) {
    return (
        <div className='base-overlay' onClick={onClick}>
            <div className="base-overlay_content" onClick={(e) => e.stopPropagation()}>
                {children}
            </div>
        </div>
    );
};